# nonagon_api/graphql/resolvers.py
"""
GraphQL Query and Mutation resolvers.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

import strawberry

from nonagon_core.domain.models.CharacterModel import Character as DCharacter
from nonagon_core.domain.models.CharacterModel import CharacterRole
from nonagon_core.domain.models.EntityIDModel import CharacterID, QuestID, SummaryID, UserID
from nonagon_core.domain.models.LookupModel import LookupEntry as DLookupEntry
from nonagon_core.domain.models.QuestModel import Quest as DQuest
from nonagon_core.domain.models.QuestModel import QuestStatus as DQuestStatus
from nonagon_core.domain.models.SummaryModel import QuestSummary as DSummary
from nonagon_core.domain.models.SummaryModel import SummaryKind as DSummaryKind
from nonagon_core.domain.models.UserModel import Role as DRole
from nonagon_core.domain.models.UserModel import User as DUser
from nonagon_core.infra.postgres.characters_repo import CharactersRepoPostgres
from nonagon_core.infra.postgres.lookup_repo import LookupRepoPostgres
from nonagon_core.infra.postgres.quests_repo import QuestsRepoPostgres
from nonagon_core.infra.postgres.summaries_repo import SummariesRepoPostgres
from nonagon_core.infra.postgres.users_repo import UsersRepoPostgres

from nonagon_api.graphql.converters import (
    domain_character_to_gql,
    domain_lookup_to_gql,
    domain_quest_to_gql,
    domain_summary_to_gql,
    domain_user_to_gql,
)
from nonagon_api.graphql.types import (
    AddSignupInput,
    Character,
    CreateCharacterInput,
    CreateLookupInput,
    CreateQuestInput,
    CreateSummaryInput,
    CreateUserInput,
    LookupEntry,
    Quest,
    Summary,
    UpdateCharacterInput,
    UpdateLookupInput,
    UpdateQuestInput,
    UpdateSummaryInput,
    UpdateUserInput,
    User,
    UserRole,
)

# Repository instances
users_repo = UsersRepoPostgres()
quests_repo = QuestsRepoPostgres()
characters_repo = CharactersRepoPostgres()
summaries_repo = SummariesRepoPostgres()
lookup_repo = LookupRepoPostgres()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_roles(raw: Optional[List[UserRole]]) -> List[DRole]:
    if not raw:
        return [DRole.MEMBER]
    seen = set()
    roles = []
    for r in raw:
        role = DRole(r.value)
        if role not in seen:
            seen.add(role)
            roles.append(role)
    return roles or [DRole.MEMBER]


# =============================================================================
# Query Resolvers
# =============================================================================

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, guild_id: int, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        user = await users_repo.get(guild_id, user_id)
        if user:
            user.guild_id = guild_id
            return domain_user_to_gql(user)
        return None

    @strawberry.field
    async def user_by_discord(self, guild_id: int, discord_id: str) -> Optional[User]:
        """Get a user by Discord ID."""
        user = await users_repo.get_by_discord_id(guild_id, discord_id)
        if user:
            user.guild_id = guild_id
            return domain_user_to_gql(user)
        return None

    @strawberry.field
    async def character(self, guild_id: int, character_id: str) -> Optional[Character]:
        """Get a character by ID."""
        char = await characters_repo.get(guild_id, character_id)
        if char:
            return domain_character_to_gql(char)
        return None

    @strawberry.field
    async def quest(self, guild_id: int, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        quest = await quests_repo.get(guild_id, quest_id)
        if quest:
            quest.guild_id = guild_id
            return domain_quest_to_gql(quest)
        return None

    @strawberry.field
    async def summary(self, guild_id: int, summary_id: str) -> Optional[Summary]:
        """Get a summary by ID."""
        summary = await summaries_repo.get(guild_id, summary_id)
        if summary:
            return domain_summary_to_gql(summary)
        return None

    @strawberry.field
    async def lookup(self, guild_id: int, name: str) -> Optional[LookupEntry]:
        """Get a lookup entry by name."""
        entry = await lookup_repo.get_by_name(guild_id, name)
        if entry:
            return domain_lookup_to_gql(entry)
        return None

    @strawberry.field
    async def lookup_search(self, guild_id: int, query: str) -> Optional[LookupEntry]:
        """Search for a lookup entry by partial name."""
        entry = await lookup_repo.find_best_match(guild_id, query)
        if entry:
            return domain_lookup_to_gql(entry)
        return None

    @strawberry.field
    async def all_lookups(self, guild_id: int) -> List[LookupEntry]:
        """Get all lookup entries for a guild."""
        entries = await lookup_repo.list_all(guild_id)
        return [domain_lookup_to_gql(e) for e in entries]


# =============================================================================
# Mutation Resolvers
# =============================================================================

@strawberry.type
class Mutation:
    # --- User Mutations ---

    @strawberry.mutation
    async def create_user(self, guild_id: int, data: CreateUserInput) -> User:
        """Create a new user."""
        raw_id = await users_repo.next_id(guild_id)
        uid = UserID.parse(raw_id)

        user = DUser(
            user_id=uid,
            guild_id=guild_id,
            discord_id=data.discord_id,
            dm_channel_id=data.dm_channel_id,
            dm_opt_in=data.dm_opt_in,
            roles=_normalize_roles(data.roles),
            joined_at=_now(),
            last_active_at=_now(),
        )

        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def update_user(self, guild_id: int, user_id: str, data: UpdateUserInput) -> User:
        """Update an existing user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id

        if data.discord_id is not strawberry.UNSET:
            user.discord_id = data.discord_id
        if data.dm_channel_id is not strawberry.UNSET:
            user.dm_channel_id = data.dm_channel_id
        if data.dm_opt_in is not strawberry.UNSET:
            user.dm_opt_in = data.dm_opt_in
        if data.roles is not strawberry.UNSET and data.roles:
            user.roles = _normalize_roles(data.roles)

        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def delete_user(self, guild_id: int, user_id: str) -> bool:
        """Delete a user."""
        return await users_repo.delete(guild_id, user_id)

    @strawberry.mutation
    async def enable_player(self, guild_id: int, user_id: str) -> User:
        """Enable the player role for a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        user.enable_player()
        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def disable_player(self, guild_id: int, user_id: str) -> User:
        """Disable the player role for a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        user.disable_player()
        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def enable_referee(self, guild_id: int, user_id: str) -> User:
        """Enable the referee role for a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        user.enable_referee()
        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def disable_referee(self, guild_id: int, user_id: str) -> User:
        """Disable the referee role for a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        user.disable_referee()
        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def link_character_to_user(
        self, guild_id: int, user_id: str, character_id: str
    ) -> User:
        """Link a character to a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        character = await characters_repo.get(guild_id, character_id)
        if not character:
            raise ValueError("Character not found")

        user.guild_id = guild_id
        if user.player is None:
            user.enable_player()

        parsed_char_id = CharacterID.parse(character_id)
        if parsed_char_id not in user.player.characters:
            user.player.characters.append(parsed_char_id)

        character.guild_id = guild_id
        character.owner_id = user.user_id
        await characters_repo.upsert(guild_id, character)

        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def unlink_character_from_user(
        self, guild_id: int, user_id: str, character_id: str
    ) -> User:
        """Unlink a character from a user."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        parsed_char_id = CharacterID.parse(character_id)

        if user.player and parsed_char_id in user.player.characters:
            user.player.characters.remove(parsed_char_id)

        user.validate_user()
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    @strawberry.mutation
    async def update_user_last_active(self, guild_id: int, user_id: str) -> User:
        """Update user's last active timestamp."""
        user = await users_repo.get(guild_id, user_id)
        if not user:
            raise ValueError("User not found")

        user.guild_id = guild_id
        user.update_last_active(_now())
        await users_repo.upsert(guild_id, user)
        return domain_user_to_gql(user)

    # --- Character Mutations ---

    @strawberry.mutation
    async def create_character(self, guild_id: int, data: CreateCharacterInput) -> Character:
        """Create a new character."""
        raw_id = await characters_repo.next_id(guild_id)

        character = DCharacter(
            character_id=raw_id,
            guild_id=guild_id,
            owner_id=UserID.parse(data.owner_id),
            name=data.name,
            ddb_link=data.ddb_link or "",
            character_thread_link=data.character_thread_link or "",
            token_link=data.token_link or "",
            art_link=data.art_link or "",
            description=data.description,
            notes=data.notes,
            tags=data.tags or [],
            created_at=_now(),
        )

        await characters_repo.upsert(guild_id, character)
        return domain_character_to_gql(character)

    @strawberry.mutation
    async def update_character(
        self, guild_id: int, character_id: str, data: UpdateCharacterInput
    ) -> Character:
        """Update an existing character."""
        character = await characters_repo.get(guild_id, character_id)
        if not character:
            raise ValueError("Character not found")

        if data.name is not strawberry.UNSET:
            character.name = data.name
        if data.ddb_link is not strawberry.UNSET:
            character.ddb_link = data.ddb_link
        if data.character_thread_link is not strawberry.UNSET:
            character.character_thread_link = data.character_thread_link
        if data.token_link is not strawberry.UNSET:
            character.token_link = data.token_link
        if data.art_link is not strawberry.UNSET:
            character.art_link = data.art_link
        if data.description is not strawberry.UNSET:
            character.description = data.description
        if data.notes is not strawberry.UNSET:
            character.notes = data.notes
        if data.tags is not strawberry.UNSET:
            character.tags = data.tags
        if data.status is not strawberry.UNSET:
            character.status = CharacterRole(data.status.value)

        await characters_repo.upsert(guild_id, character)
        return domain_character_to_gql(character)

    @strawberry.mutation
    async def delete_character(self, guild_id: int, character_id: str) -> bool:
        """Delete a character."""
        return await characters_repo.delete(guild_id, character_id)

    # --- Quest Mutations ---

    @strawberry.mutation
    async def create_quest(self, guild_id: int, data: CreateQuestInput) -> Quest:
        """Create a new quest."""
        raw_id = await quests_repo.next_id(guild_id)
        quest_id = QuestID.parse(raw_id)
        referee_id = UserID.parse(data.referee_id)

        # Verify referee exists and has referee role
        referee = await users_repo.get(guild_id, data.referee_id)
        if not referee or not referee.is_referee:
            raise ValueError("Referee not found or lacks permissions")

        quest = DQuest(
            quest_id=quest_id,
            guild_id=guild_id,
            referee_id=referee_id,
            channel_id=data.channel_id,
            message_id=data.message_id,
            raw=data.raw,
            title=data.title,
            description=data.description,
            starting_at=data.starting_at,
            duration=timedelta(hours=data.duration_hours) if data.duration_hours else None,
            image_url=data.image_url,
            linked_quests=[QuestID.parse(q) for q in (data.linked_quests or [])],
            linked_summaries=[SummaryID.parse(s) for s in (data.linked_summaries or [])],
            status=DQuestStatus.ANNOUNCED,
        )

        quest.validate_quest()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def update_quest(self, guild_id: int, quest_id: str, data: UpdateQuestInput) -> Quest:
        """Update an existing quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id

        if data.title is not strawberry.UNSET:
            quest.title = data.title
        if data.description is not strawberry.UNSET:
            quest.description = data.description
        if data.starting_at is not strawberry.UNSET:
            quest.starting_at = data.starting_at
        if data.duration_hours is not strawberry.UNSET:
            quest.duration = timedelta(hours=data.duration_hours) if data.duration_hours else None
        if data.image_url is not strawberry.UNSET:
            quest.image_url = data.image_url
        if data.linked_quests is not strawberry.UNSET:
            quest.linked_quests = [QuestID.parse(q) for q in (data.linked_quests or [])]
        if data.linked_summaries is not strawberry.UNSET:
            quest.linked_summaries = [SummaryID.parse(s) for s in (data.linked_summaries or [])]

        quest.validate_quest()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def delete_quest(self, guild_id: int, quest_id: str) -> bool:
        """Delete a quest."""
        return await quests_repo.delete(guild_id, quest_id)

    @strawberry.mutation
    async def add_quest_signup(
        self, guild_id: int, quest_id: str, data: AddSignupInput
    ) -> Quest:
        """Add a signup to a quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        user_id = UserID.parse(data.user_id)
        character_id = CharacterID.parse(data.character_id)

        # Verify user exists and is a player
        user = await users_repo.get(guild_id, data.user_id)
        if not user or not user.is_player:
            raise ValueError("User not found or is not a player")

        # Verify character exists and belongs to user
        character = await characters_repo.get(guild_id, data.character_id)
        if not character:
            raise ValueError("Character not found")
        if not user.is_character_owner(character_id):
            raise ValueError("Character does not belong to user")

        if not quest.is_signup_open:
            raise ValueError("Signups are closed for this quest")

        quest.guild_id = guild_id
        quest.add_signup(user_id, character_id)
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def remove_quest_signup(self, guild_id: int, quest_id: str, user_id: str) -> Quest:
        """Remove a signup from a quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.remove_signup(UserID.parse(user_id))
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def select_quest_signup(self, guild_id: int, quest_id: str, user_id: str) -> Quest:
        """Select a signup for a quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.select_signup(UserID.parse(user_id))
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def close_quest_signups(self, guild_id: int, quest_id: str) -> Quest:
        """Close signups for a quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.close_signups()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def complete_quest(self, guild_id: int, quest_id: str) -> Quest:
        """Mark a quest as completed."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.set_completed()
        quest.ended_at = _now()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def cancel_quest(self, guild_id: int, quest_id: str) -> Quest:
        """Mark a quest as cancelled."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.set_cancelled()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    @strawberry.mutation
    async def nudge_quest(self, guild_id: int, quest_id: str) -> Quest:
        """Update the last nudged timestamp for a quest."""
        quest = await quests_repo.get(guild_id, quest_id)
        if not quest:
            raise ValueError("Quest not found")

        quest.guild_id = guild_id
        quest.last_nudged_at = _now()
        await quests_repo.upsert(guild_id, quest)
        return domain_quest_to_gql(quest)

    # --- Summary Mutations ---

    @strawberry.mutation
    async def create_summary(self, guild_id: int, data: CreateSummaryInput) -> Summary:
        """Create a new summary."""
        raw_id = await summaries_repo.next_id(guild_id)
        summary_id = SummaryID.parse(raw_id)

        summary = DSummary(
            summary_id=summary_id,
            guild_id=guild_id,
            kind=DSummaryKind(data.kind.value),
            author_id=UserID.parse(data.author_id),
            character_id=CharacterID.parse(data.character_id) if data.character_id else None,
            quest_id=QuestID.parse(data.quest_id) if data.quest_id else None,
            raw=data.raw,
            title=data.title,
            description=data.description,
            characters=[CharacterID.parse(c) for c in (data.characters or [])],
            players=[UserID.parse(p) for p in (data.players or [])],
            created_on=_now(),
        )

        summary.validate_summary()
        await summaries_repo.upsert(guild_id, summary)
        return domain_summary_to_gql(summary)

    @strawberry.mutation
    async def update_summary(
        self, guild_id: int, summary_id: str, data: UpdateSummaryInput
    ) -> Summary:
        """Update an existing summary."""
        summary = await summaries_repo.get(guild_id, summary_id)
        if not summary:
            raise ValueError("Summary not found")

        if data.title is not strawberry.UNSET:
            summary.title = data.title
        if data.description is not strawberry.UNSET:
            summary.description = data.description
        if data.raw is not strawberry.UNSET:
            summary.raw = data.raw
        if data.characters is not strawberry.UNSET:
            summary.characters = [CharacterID.parse(c) for c in (data.characters or [])]
        if data.players is not strawberry.UNSET:
            summary.players = [UserID.parse(p) for p in (data.players or [])]

        summary.last_edited_at = _now()
        summary.validate_summary()
        await summaries_repo.upsert(guild_id, summary)
        return domain_summary_to_gql(summary)

    @strawberry.mutation
    async def delete_summary(self, guild_id: int, summary_id: str) -> bool:
        """Delete a summary."""
        return await summaries_repo.delete(guild_id, summary_id)

    # --- Lookup Mutations ---

    @strawberry.mutation
    async def create_lookup(
        self, guild_id: int, created_by: int, data: CreateLookupInput
    ) -> LookupEntry:
        """Create a new lookup entry."""
        entry = DLookupEntry(
            guild_id=guild_id,
            name=data.name,
            url=data.url,
            created_by=created_by,
            description=data.description,
        )

        entry.validate_entry()
        result = await lookup_repo.upsert(entry)
        return domain_lookup_to_gql(result)

    @strawberry.mutation
    async def update_lookup(
        self, guild_id: int, name: str, updated_by: int, data: UpdateLookupInput
    ) -> LookupEntry:
        """Update an existing lookup entry."""
        entry = await lookup_repo.get_by_name(guild_id, name)
        if not entry:
            raise ValueError("Lookup entry not found")

        if data.url is not strawberry.UNSET:
            entry.url = data.url
        if data.description is not strawberry.UNSET:
            entry.description = data.description

        entry.touch_updated(updated_by)
        entry.validate_entry()
        result = await lookup_repo.upsert(entry)
        return domain_lookup_to_gql(result)

    @strawberry.mutation
    async def delete_lookup(self, guild_id: int, name: str) -> bool:
        """Delete a lookup entry."""
        return await lookup_repo.delete(guild_id, name)
