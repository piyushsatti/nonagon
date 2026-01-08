# nonagon_bot/services/graphql_client.py
"""
GraphQL client for bot-to-API communication.

This module provides async functions for the bot to call the GraphQL API
instead of the deprecated REST endpoints.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import aiohttp

from nonagon_bot.utils.logging import get_logger

logger = get_logger(__name__)

GRAPHQL_API_URL = os.getenv("GRAPHQL_API_URL", "http://localhost:8000/graphql")
GRAPHQL_API_TOKEN = os.getenv("GRAPHQL_API_TOKEN", "")


class GraphQLError(Exception):
    """Raised when the GraphQL API returns errors."""
    
    def __init__(self, errors: List[Dict[str, Any]], data: Optional[Dict[str, Any]] = None):
        self.errors = errors
        self.data = data
        messages = [e.get("message", str(e)) for e in errors]
        super().__init__(f"GraphQL errors: {'; '.join(messages)}")


async def _execute_graphql(
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    *,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Execute a GraphQL query/mutation and return the data."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    headers = {"Content-Type": "application/json"}
    token = GRAPHQL_API_TOKEN.strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            GRAPHQL_API_URL,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as response:
            result = await response.json()

    if "errors" in result and result["errors"]:
        raise GraphQLError(result["errors"], result.get("data"))

    return result.get("data", {})


# ─────────────────────────────────────────────────────────────────────────────
# Quest Mutations (replacing REST _*_via_api methods)
# ─────────────────────────────────────────────────────────────────────────────

ADD_QUEST_SIGNUP_MUTATION = """
mutation AddQuestSignup($guildId: Int!, $questId: String!, $data: AddSignupInput!) {
    addQuestSignup(guildId: $guildId, questId: $questId, data: $data) {
        questId
        signups {
            userId
            characterId
            status
        }
    }
}
"""


async def signup_quest(
    guild_id: int,
    quest_id: str,
    user_id: str,
    character_id: str,
) -> Dict[str, Any]:
    """Add a signup to a quest via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
        "data": {
            "userId": user_id,
            "characterId": character_id,
        },
    }
    data = await _execute_graphql(ADD_QUEST_SIGNUP_MUTATION, variables)
    return data.get("addQuestSignup", {})


REMOVE_QUEST_SIGNUP_MUTATION = """
mutation RemoveQuestSignup($guildId: Int!, $questId: String!, $userId: String!) {
    removeQuestSignup(guildId: $guildId, questId: $questId, userId: $userId) {
        questId
        signups {
            userId
            characterId
            status
        }
    }
}
"""


async def remove_signup(
    guild_id: int,
    quest_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """Remove a signup from a quest via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
        "userId": user_id,
    }
    data = await _execute_graphql(REMOVE_QUEST_SIGNUP_MUTATION, variables)
    return data.get("removeQuestSignup", {})


SELECT_QUEST_SIGNUP_MUTATION = """
mutation SelectQuestSignup($guildId: Int!, $questId: String!, $userId: String!) {
    selectQuestSignup(guildId: $guildId, questId: $questId, userId: $userId) {
        questId
        signups {
            userId
            characterId
            status
        }
    }
}
"""


async def select_signup(
    guild_id: int,
    quest_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """Select/accept a signup for a quest via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
        "userId": user_id,
    }
    data = await _execute_graphql(SELECT_QUEST_SIGNUP_MUTATION, variables)
    return data.get("selectQuestSignup", {})


NUDGE_QUEST_MUTATION = """
mutation NudgeQuest($guildId: Int!, $questId: String!) {
    nudgeQuest(guildId: $guildId, questId: $questId) {
        questId
        status
    }
}
"""


async def nudge_quest(
    guild_id: int,
    quest_id: str,
) -> Dict[str, Any]:
    """Nudge/remind quest participants via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
    }
    data = await _execute_graphql(NUDGE_QUEST_MUTATION, variables)
    return data.get("nudgeQuest", {})


CLOSE_QUEST_SIGNUPS_MUTATION = """
mutation CloseQuestSignups($guildId: Int!, $questId: String!) {
    closeQuestSignups(guildId: $guildId, questId: $questId) {
        questId
        isSignupOpen
        status
    }
}
"""


async def close_signups(
    guild_id: int,
    quest_id: str,
) -> Dict[str, Any]:
    """Close signups for a quest via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
    }
    data = await _execute_graphql(CLOSE_QUEST_SIGNUPS_MUTATION, variables)
    return data.get("closeQuestSignups", {})


# ─────────────────────────────────────────────────────────────────────────────
# Quest Queries
# ─────────────────────────────────────────────────────────────────────────────

GET_QUEST_QUERY = """
query GetQuest($guildId: Int!, $questId: String!) {
    quest(guildId: $guildId, questId: $questId) {
        questId
        guildId
        refereeId
        channelId
        messageId
        raw
        title
        description
        startingAt
        durationHours
        imageUrl
        status
        announceAt
        startedAt
        endedAt
        isSignupOpen
        signups {
            userId
            characterId
            status
        }
    }
}
"""


async def get_quest(
    guild_id: int,
    quest_id: str,
) -> Optional[Dict[str, Any]]:
    """Fetch a quest by ID via GraphQL API."""
    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
    }
    try:
        data = await _execute_graphql(GET_QUEST_QUERY, variables)
        return data.get("quest")
    except GraphQLError as e:
        logger.warning("Failed to fetch quest %s: %s", quest_id, e)
        return None


LIST_QUESTS_QUERY = """
query ListQuests($guildId: Int!, $status: String) {
    quests(guildId: $guildId, status: $status) {
        questId
        title
        status
        startingAt
        refereeId
        isSignupOpen
    }
}
"""


async def list_quests(
    guild_id: int,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List quests for a guild via GraphQL API."""
    variables: Dict[str, Any] = {"guildId": int(guild_id)}
    if status:
        variables["status"] = status
    try:
        data = await _execute_graphql(LIST_QUESTS_QUERY, variables)
        return data.get("quests", [])
    except GraphQLError as e:
        logger.warning("Failed to list quests: %s", e)
        return []

# ─────────────────────────────────────────────────────────────────────────────
# Additional Queries (users, characters, pending/recent quests)
# ─────────────────────────────────────────────────────────────────────────────

LIST_USERS_BY_GUILD_QUERY = """
query ListUsersByGuild($guildId: Int!) {
    usersByGuild(guildId: $guildId) {
        userId
        discordId
        roles
        dmOptIn
        lastActiveAt
        messagesCountTotal
        reactionsGiven
        reactionsReceived
        voiceTotalTimeSpent
    }
}
"""


async def list_users_by_guild(guild_id: int) -> List[Dict[str, Any]]:
    variables = {"guildId": int(guild_id)}
    try:
        data = await _execute_graphql(LIST_USERS_BY_GUILD_QUERY, variables)
        return data.get("usersByGuild", [])
    except GraphQLError as e:
        logger.warning("Failed to list users: %s", e)
        return []


LIST_CHARACTERS_BY_OWNER_QUERY = """
query ListCharactersByOwner($guildId: Int!, $ownerId: String!) {
    charactersByOwner(guildId: $guildId, ownerId: $ownerId) {
        characterId
        name
        status
        ownerId
    }
}
"""


async def list_characters_by_owner(guild_id: int, owner_id: str) -> List[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "ownerId": owner_id}
    try:
        data = await _execute_graphql(LIST_CHARACTERS_BY_OWNER_QUERY, variables)
        return data.get("charactersByOwner", [])
    except GraphQLError as e:
        logger.warning("Failed to list characters: %s", e)
        return []


PENDING_QUESTS_QUERY = """
query PendingQuests($guildId: Int!, $before: DateTime) {
    pendingQuests(guildId: $guildId, before: $before) {
        questId
        title
        status
        announceAt
    }
}
"""


async def list_pending_quests(guild_id: int, before_iso: Optional[str] = None) -> List[Dict[str, Any]]:
    variables: Dict[str, Any] = {"guildId": int(guild_id)}
    if before_iso:
        variables["before"] = before_iso
    try:
        data = await _execute_graphql(PENDING_QUESTS_QUERY, variables)
        return data.get("pendingQuests", [])
    except GraphQLError as e:
        logger.warning("Failed to list pending quests: %s", e)
        return []


RECENT_QUESTS_QUERY = """
query RecentQuests($guildId: Int!, $limit: Int) {
    recentQuests(guildId: $guildId, limit: $limit) {
        questId
        title
        status
        startingAt
    }
}
"""


async def list_recent_quests(guild_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "limit": int(limit)}
    try:
        data = await _execute_graphql(RECENT_QUESTS_QUERY, variables)
        return data.get("recentQuests", [])
    except GraphQLError as e:
        logger.warning("Failed to list recent quests: %s", e)
        return []

# ─────────────────────────────────────────────────────────────────────────────
# User Queries/Mutations
# ─────────────────────────────────────────────────────────────────────────────

GET_USER_BY_DISCORD_QUERY = """
query UserByDiscord($guildId: Int!, $discordId: String!) {
    userByDiscord(guildId: $guildId, discordId: $discordId) {
        userId
        guildId
        discordId
        roles
        dmOptIn
        lastActiveAt
        messagesCountTotal
        reactionsGiven
        reactionsReceived
        voiceTotalTimeSpent
    }
}
"""


async def get_user_by_discord(guild_id: int, discord_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "discordId": str(discord_id)}
    try:
        data = await _execute_graphql(GET_USER_BY_DISCORD_QUERY, variables)
        return data.get("userByDiscord")
    except GraphQLError as e:
        logger.warning("Failed to fetch user by discord: %s", e)
        return None


CREATE_USER_MUTATION = """
mutation CreateUser($guildId: Int!, $data: CreateUserInput!) {
    createUser(guildId: $guildId, data: $data) {
        userId
        discordId
        roles
    }
}
"""


async def create_user(
    guild_id: int,
    discord_id: str,
    dm_channel_id: Optional[str] = None,
    dm_opt_in: bool = True,
    roles: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    variables = {
        "guildId": int(guild_id),
        "data": {
            "discordId": discord_id,
            "dmChannelId": dm_channel_id,
            "dmOptIn": dm_opt_in,
            "roles": roles or [],
        },
    }
    try:
        data = await _execute_graphql(CREATE_USER_MUTATION, variables)
        return data.get("createUser")
    except GraphQLError as e:
        logger.warning("Failed to create user: %s", e)
        return None


UPDATE_USER_MUTATION = """
mutation UpdateUser($guildId: Int!, $userId: String!, $data: UpdateUserInput!) {
    updateUser(guildId: $guildId, userId: $userId, data: $data) {
        userId
        discordId
        roles
    }
}
"""


async def update_user(
    guild_id: int,
    user_id: str,
    *,
    dm_channel_id: Optional[str] = None,
    dm_opt_in: Optional[bool] = None,
    roles: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if dm_channel_id is not None:
        payload["dmChannelId"] = dm_channel_id
    if dm_opt_in is not None:
        payload["dmOptIn"] = dm_opt_in
    if roles is not None:
        payload["roles"] = roles
    if not payload:
        return None

    variables = {
        "guildId": int(guild_id),
        "userId": user_id,
        "data": payload,
    }
    try:
        data = await _execute_graphql(UPDATE_USER_MUTATION, variables)
        return data.get("updateUser")
    except GraphQLError as e:
        logger.warning("Failed to update user: %s", e)
        return None


DELETE_USER_MUTATION = """
mutation DeleteUser($guildId: Int!, $userId: String!) {
    deleteUser(guildId: $guildId, userId: $userId)
}
"""


async def delete_user(guild_id: int, user_id: str) -> bool:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(DELETE_USER_MUTATION, variables)
        return bool(data.get("deleteUser"))
    except GraphQLError as e:
        logger.warning("Failed to delete user: %s", e)
        return False


ENABLE_PLAYER_MUTATION = """
mutation EnablePlayer($guildId: Int!, $userId: String!) {
    enablePlayer(guildId: $guildId, userId: $userId) {
        userId
        roles
    }
}
"""


DISABLE_PLAYER_MUTATION = """
mutation DisablePlayer($guildId: Int!, $userId: String!) {
    disablePlayer(guildId: $guildId, userId: $userId) {
        userId
        roles
    }
}
"""


async def enable_player(guild_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(ENABLE_PLAYER_MUTATION, variables)
        return data.get("enablePlayer")
    except GraphQLError as e:
        logger.warning("Failed to enable player role: %s", e)
        return None


async def disable_player(guild_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(DISABLE_PLAYER_MUTATION, variables)
        return data.get("disablePlayer")
    except GraphQLError as e:
        logger.warning("Failed to disable player role: %s", e)
        return None


ENABLE_REFEREE_MUTATION = """
mutation EnableReferee($guildId: Int!, $userId: String!) {
    enableReferee(guildId: $guildId, userId: $userId) {
        userId
        roles
    }
}
"""


DISABLE_REFEREE_MUTATION = """
mutation DisableReferee($guildId: Int!, $userId: String!) {
    disableReferee(guildId: $guildId, userId: $userId) {
        userId
        roles
    }
}
"""


async def enable_referee(guild_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(ENABLE_REFEREE_MUTATION, variables)
        return data.get("enableReferee")
    except GraphQLError as e:
        logger.warning("Failed to enable referee role: %s", e)
        return None


async def disable_referee(guild_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(DISABLE_REFEREE_MUTATION, variables)
        return data.get("disableReferee")
    except GraphQLError as e:
        logger.warning("Failed to disable referee role: %s", e)
        return None


LINK_CHARACTER_TO_USER_MUTATION = """
mutation LinkCharacterToUser($guildId: Int!, $userId: String!, $characterId: String!) {
    linkCharacterToUser(guildId: $guildId, userId: $userId, characterId: $characterId) {
        userId
        roles
    }
}
"""


UNLINK_CHARACTER_FROM_USER_MUTATION = """
mutation UnlinkCharacterFromUser($guildId: Int!, $userId: String!, $characterId: String!) {
    unlinkCharacterFromUser(guildId: $guildId, userId: $userId, characterId: $characterId) {
        userId
        roles
    }
}
"""


async def link_character_to_user(
    guild_id: int, user_id: str, character_id: str
) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id, "characterId": character_id}
    try:
        data = await _execute_graphql(LINK_CHARACTER_TO_USER_MUTATION, variables)
        return data.get("linkCharacterToUser")
    except GraphQLError as e:
        logger.warning("Failed to link character to user: %s", e)
        return None


async def unlink_character_from_user(
    guild_id: int, user_id: str, character_id: str
) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id, "characterId": character_id}
    try:
        data = await _execute_graphql(UNLINK_CHARACTER_FROM_USER_MUTATION, variables)
        return data.get("unlinkCharacterFromUser")
    except GraphQLError as e:
        logger.warning("Failed to unlink character from user: %s", e)
        return None


UPDATE_USER_LAST_ACTIVE_MUTATION = """
mutation UpdateUserLastActive($guildId: Int!, $userId: String!) {
    updateUserLastActive(guildId: $guildId, userId: $userId) {
        userId
        lastActiveAt
    }
}
"""


async def update_user_last_active(guild_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "userId": user_id}
    try:
        data = await _execute_graphql(UPDATE_USER_LAST_ACTIVE_MUTATION, variables)
        return data.get("updateUserLastActive")
    except GraphQLError as e:
        logger.warning("Failed to update user last active: %s", e)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Character Mutations
# ─────────────────────────────────────────────────────────────────────────────

CREATE_CHARACTER_MUTATION = """
mutation CreateCharacter($guildId: Int!, $data: CreateCharacterInput!) {
    createCharacter(guildId: $guildId, data: $data) {
        characterId
        ownerId
        name
        status
    }
}
"""


async def create_character(
    guild_id: int,
    *,
    owner_id: str,
    name: str,
    ddb_link: Optional[str] = None,
    character_thread_link: Optional[str] = None,
    token_link: Optional[str] = None,
    art_link: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    variables: Dict[str, Any] = {
        "guildId": int(guild_id),
        "data": {
            "ownerId": owner_id,
            "name": name,
            "ddbLink": ddb_link,
            "characterThreadLink": character_thread_link,
            "tokenLink": token_link,
            "artLink": art_link,
            "description": description,
            "notes": notes,
            "tags": tags or [],
        },
    }
    try:
        data = await _execute_graphql(CREATE_CHARACTER_MUTATION, variables)
        return data.get("createCharacter")
    except GraphQLError as e:
        logger.warning("Failed to create character: %s", e)
        return None


UPDATE_CHARACTER_MUTATION = """
mutation UpdateCharacter($guildId: Int!, $characterId: String!, $data: UpdateCharacterInput!) {
    updateCharacter(guildId: $guildId, characterId: $characterId, data: $data) {
        characterId
        ownerId
        name
        status
    }
}
"""


async def update_character(
    guild_id: int,
    character_id: str,
    *,
    name: Optional[str] = None,
    ddb_link: Optional[str] = None,
    character_thread_link: Optional[str] = None,
    token_link: Optional[str] = None,
    art_link: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if ddb_link is not None:
        payload["ddbLink"] = ddb_link
    if character_thread_link is not None:
        payload["characterThreadLink"] = character_thread_link
    if token_link is not None:
        payload["tokenLink"] = token_link
    if art_link is not None:
        payload["artLink"] = art_link
    if description is not None:
        payload["description"] = description
    if notes is not None:
        payload["notes"] = notes
    if tags is not None:
        payload["tags"] = tags
    if status is not None:
        payload["status"] = status
    if not payload:
        return None

    variables = {
        "guildId": int(guild_id),
        "characterId": character_id,
        "data": payload,
    }
    try:
        data = await _execute_graphql(UPDATE_CHARACTER_MUTATION, variables)
        return data.get("updateCharacter")
    except GraphQLError as e:
        logger.warning("Failed to update character: %s", e)
        return None


DELETE_CHARACTER_MUTATION = """
mutation DeleteCharacter($guildId: Int!, $characterId: String!) {
    deleteCharacter(guildId: $guildId, characterId: $characterId)
}
"""


async def delete_character(guild_id: int, character_id: str) -> bool:
    variables = {"guildId": int(guild_id), "characterId": character_id}
    try:
        data = await _execute_graphql(DELETE_CHARACTER_MUTATION, variables)
        return bool(data.get("deleteCharacter"))
    except GraphQLError as e:
        logger.warning("Failed to delete character: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Quest Mutations (create/update/delete)
# ─────────────────────────────────────────────────────────────────────────────

CREATE_QUEST_MUTATION = """
mutation CreateQuest($guildId: Int!, $data: CreateQuestInput!) {
    createQuest(guildId: $guildId, data: $data) {
        questId
        refereeId
        title
        status
    }
}
"""


async def create_quest(
    guild_id: int,
    *,
    referee_id: str,
    raw: str,
    channel_id: str,
    message_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    starting_at: Optional[str] = None,
    duration_hours: Optional[int] = None,
    image_url: Optional[str] = None,
    linked_quests: Optional[List[str]] = None,
    linked_summaries: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    variables: Dict[str, Any] = {
        "guildId": int(guild_id),
        "data": {
            "refereeId": referee_id,
            "raw": raw,
            "channelId": channel_id,
            "messageId": message_id,
            "title": title,
            "description": description,
            "startingAt": starting_at,
            "durationHours": duration_hours,
            "imageUrl": image_url,
            "linkedQuests": linked_quests or [],
            "linkedSummaries": linked_summaries or [],
        },
    }
    try:
        data = await _execute_graphql(CREATE_QUEST_MUTATION, variables)
        return data.get("createQuest")
    except GraphQLError as e:
        logger.warning("Failed to create quest: %s", e)
        return None


UPDATE_QUEST_MUTATION = """
mutation UpdateQuest($guildId: Int!, $questId: String!, $data: UpdateQuestInput!) {
    updateQuest(guildId: $guildId, questId: $questId, data: $data) {
        questId
        title
        status
    }
}
"""


async def update_quest(
    guild_id: int,
    quest_id: str,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    starting_at: Optional[str] = None,
    duration_hours: Optional[int] = None,
    image_url: Optional[str] = None,
    linked_quests: Optional[List[str]] = None,
    linked_summaries: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if starting_at is not None:
        payload["startingAt"] = starting_at
    if duration_hours is not None:
        payload["durationHours"] = duration_hours
    if image_url is not None:
        payload["imageUrl"] = image_url
    if linked_quests is not None:
        payload["linkedQuests"] = linked_quests
    if linked_summaries is not None:
        payload["linkedSummaries"] = linked_summaries
    if not payload:
        return None

    variables = {
        "guildId": int(guild_id),
        "questId": quest_id,
        "data": payload,
    }
    try:
        data = await _execute_graphql(UPDATE_QUEST_MUTATION, variables)
        return data.get("updateQuest")
    except GraphQLError as e:
        logger.warning("Failed to update quest: %s", e)
        return None


DELETE_QUEST_MUTATION = """
mutation DeleteQuest($guildId: Int!, $questId: String!) {
    deleteQuest(guildId: $guildId, questId: $questId)
}
"""


async def delete_quest(guild_id: int, quest_id: str) -> bool:
    variables = {"guildId": int(guild_id), "questId": quest_id}
    try:
        data = await _execute_graphql(DELETE_QUEST_MUTATION, variables)
        return bool(data.get("deleteQuest"))
    except GraphQLError as e:
        logger.warning("Failed to delete quest: %s", e)
        return False


COMPLETE_QUEST_MUTATION = """
mutation CompleteQuest($guildId: Int!, $questId: String!) {
    completeQuest(guildId: $guildId, questId: $questId) {
        questId
        status
    }
}
"""


CANCEL_QUEST_MUTATION = """
mutation CancelQuest($guildId: Int!, $questId: String!) {
    cancelQuest(guildId: $guildId, questId: $questId) {
        questId
        status
    }
}
"""


async def complete_quest(guild_id: int, quest_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "questId": quest_id}
    try:
        data = await _execute_graphql(COMPLETE_QUEST_MUTATION, variables)
        return data.get("completeQuest")
    except GraphQLError as e:
        logger.warning("Failed to complete quest: %s", e)
        return None


async def cancel_quest(guild_id: int, quest_id: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "questId": quest_id}
    try:
        data = await _execute_graphql(CANCEL_QUEST_MUTATION, variables)
        return data.get("cancelQuest")
    except GraphQLError as e:
        logger.warning("Failed to cancel quest: %s", e)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Summary Mutations
# ─────────────────────────────────────────────────────────────────────────────

CREATE_SUMMARY_MUTATION = """
mutation CreateSummary($guildId: Int!, $data: CreateSummaryInput!) {
    createSummary(guildId: $guildId, data: $data) {
        summaryId
        title
        status
    }
}
"""


async def create_summary(
    guild_id: int,
    *,
    kind: str,
    author_id: str,
    title: str,
    description: str,
    raw: Optional[str] = None,
    character_id: Optional[str] = None,
    quest_id: Optional[str] = None,
    characters: Optional[List[str]] = None,
    players: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    variables: Dict[str, Any] = {
        "guildId": int(guild_id),
        "data": {
            "kind": kind,
            "authorId": author_id,
            "title": title,
            "description": description,
            "raw": raw,
            "characterId": character_id,
            "questId": quest_id,
            "characters": characters or [],
            "players": players or [],
        },
    }
    try:
        data = await _execute_graphql(CREATE_SUMMARY_MUTATION, variables)
        return data.get("createSummary")
    except GraphQLError as e:
        logger.warning("Failed to create summary: %s", e)
        return None


UPDATE_SUMMARY_MUTATION = """
mutation UpdateSummary($guildId: Int!, $summaryId: String!, $data: UpdateSummaryInput!) {
    updateSummary(guildId: $guildId, summaryId: $summaryId, data: $data) {
        summaryId
        title
        status
    }
}
"""


async def update_summary(
    guild_id: int,
    summary_id: str,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    raw: Optional[str] = None,
    characters: Optional[List[str]] = None,
    players: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if raw is not None:
        payload["raw"] = raw
    if characters is not None:
        payload["characters"] = characters
    if players is not None:
        payload["players"] = players
    if not payload:
        return None

    variables = {
        "guildId": int(guild_id),
        "summaryId": summary_id,
        "data": payload,
    }
    try:
        data = await _execute_graphql(UPDATE_SUMMARY_MUTATION, variables)
        return data.get("updateSummary")
    except GraphQLError as e:
        logger.warning("Failed to update summary: %s", e)
        return None


DELETE_SUMMARY_MUTATION = """
mutation DeleteSummary($guildId: Int!, $summaryId: String!) {
    deleteSummary(guildId: $guildId, summaryId: $summaryId)
}
"""


async def delete_summary(guild_id: int, summary_id: str) -> bool:
    variables = {"guildId": int(guild_id), "summaryId": summary_id}
    try:
        data = await _execute_graphql(DELETE_SUMMARY_MUTATION, variables)
        return bool(data.get("deleteSummary"))
    except GraphQLError as e:
        logger.warning("Failed to delete summary: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Lookup Mutations
# ─────────────────────────────────────────────────────────────────────────────

CREATE_LOOKUP_MUTATION = """
mutation CreateLookup($guildId: Int!, $createdBy: Int!, $data: CreateLookupInput!) {
    createLookup(guildId: $guildId, createdBy: $createdBy, data: $data) {
        name
        url
        description
    }
}
"""


async def create_lookup(
    guild_id: int,
    *,
    created_by: int,
    name: str,
    url: str,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    variables = {
        "guildId": int(guild_id),
        "createdBy": int(created_by),
        "data": {"name": name, "url": url, "description": description},
    }
    try:
        data = await _execute_graphql(CREATE_LOOKUP_MUTATION, variables)
        return data.get("createLookup")
    except GraphQLError as e:
        logger.warning("Failed to create lookup: %s", e)
        return None


UPDATE_LOOKUP_MUTATION = """
mutation UpdateLookup($guildId: Int!, $name: String!, $updatedBy: Int!, $data: UpdateLookupInput!) {
    updateLookup(guildId: $guildId, name: $name, updatedBy: $updatedBy, data: $data) {
        name
        url
        description
    }
}
"""


async def update_lookup(
    guild_id: int,
    name: str,
    *,
    updated_by: int,
    url: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    payload: Dict[str, Any] = {}
    if url is not None:
        payload["url"] = url
    if description is not None:
        payload["description"] = description
    if not payload:
        return None

    variables = {
        "guildId": int(guild_id),
        "name": name,
        "updatedBy": int(updated_by),
        "data": payload,
    }
    try:
        data = await _execute_graphql(UPDATE_LOOKUP_MUTATION, variables)
        return data.get("updateLookup")
    except GraphQLError as e:
        logger.warning("Failed to update lookup: %s", e)
        return None


DELETE_LOOKUP_MUTATION = """
mutation DeleteLookup($guildId: Int!, $name: String!) {
    deleteLookup(guildId: $guildId, name: $name)
}
"""


async def delete_lookup(guild_id: int, name: str) -> bool:
    variables = {"guildId": int(guild_id), "name": name}
    try:
        data = await _execute_graphql(DELETE_LOOKUP_MUTATION, variables)
        return bool(data.get("deleteLookup"))
    except GraphQLError as e:
        logger.warning("Failed to delete lookup: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Lookup Queries
# ─────────────────────────────────────────────────────────────────────────────

GET_LOOKUP_QUERY = """
query GetLookup($guildId: Int!, $name: String!) {
    lookup(guildId: $guildId, name: $name) {
        name
        url
        description
        updatedAt
    }
}
"""


async def get_lookup(guild_id: int, name: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "name": name}
    try:
        data = await _execute_graphql(GET_LOOKUP_QUERY, variables)
        return data.get("lookup")
    except GraphQLError as e:
        logger.warning("Failed to fetch lookup: %s", e)
        return None


ALL_LOOKUPS_QUERY = """
query AllLookups($guildId: Int!) {
    allLookups(guildId: $guildId) {
        name
        url
        description
    }
}
"""


async def list_all_lookups(guild_id: int) -> List[Dict[str, Any]]:
    variables = {"guildId": int(guild_id)}
    try:
        data = await _execute_graphql(ALL_LOOKUPS_QUERY, variables)
        return data.get("allLookups", [])
    except GraphQLError as e:
        logger.warning("Failed to list lookups: %s", e)
        return []


LOOKUP_SEARCH_QUERY = """
query LookupSearch($guildId: Int!, $query: String!) {
    lookupSearch(guildId: $guildId, query: $query) {
        name
        url
        description
    }
}
"""


async def lookup_search(guild_id: int, query: str) -> Optional[Dict[str, Any]]:
    variables = {"guildId": int(guild_id), "query": query}
    try:
        data = await _execute_graphql(LOOKUP_SEARCH_QUERY, variables)
        return data.get("lookupSearch")
    except GraphQLError as e:
        logger.warning("Failed to search lookup: %s", e)
        return None
