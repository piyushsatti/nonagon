#!/usr/bin/env python3
"""
Seed script to populate demo data in PostgreSQL.

This script creates sample data for the "demo" guild (ID: 99999) that mirrors
the frontend dummy data structure. Run this to set up a working demo environment.

Usage:
    python -m backend.scripts.seed_demo
    # or
    cd backend && python scripts/seed_demo.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend paths to sys.path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "api"))
sys.path.insert(0, str(backend_root / "bot"))

from dotenv import load_dotenv
load_dotenv()

from nonagon_bot.core.domain.models.CharacterModel import Character, CharacterRole
from nonagon_bot.core.domain.models.EntityIDModel import CharacterID, QuestID, SummaryID, UserID
from nonagon_bot.core.domain.models.LookupModel import LookupEntry
from nonagon_bot.core.domain.models.QuestModel import PlayerSignUp, PlayerStatus, Quest, QuestStatus
from nonagon_bot.core.domain.models.SummaryModel import QuestSummary, SummaryKind, SummaryStatus
from nonagon_bot.core.domain.models.UserModel import Player, Referee, Role, User
from nonagon_bot.core.infra.postgres.characters_repo import CharactersRepoPostgres
from nonagon_bot.core.infra.postgres.database import close_db, init_db
from nonagon_bot.core.infra.postgres.lookup_repo import LookupRepoPostgres
from nonagon_bot.core.infra.postgres.quests_repo import QuestsRepoPostgres
from nonagon_bot.core.infra.postgres.summaries_repo import SummariesRepoPostgres
from nonagon_bot.core.infra.postgres.users_repo import UsersRepoPostgres

# Demo guild ID - must match frontend DEMO_GUILD_ID
DEMO_GUILD_ID = 99999


def parse_datetime(iso_string: str) -> datetime:
    """Parse ISO datetime string to timezone-aware datetime."""
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ============================================================================
# Demo Data Definitions
# ============================================================================

DEMO_USERS = [
    {
        "discord_id": "123456789012345678",
        "roles": [Role.MEMBER, Role.PLAYER],
        "has_server_tag": True,
        "dm_opt_in": True,
        "joined_at": "2024-01-15T10:30:00Z",
        "last_active_at": "2026-01-05T18:45:00Z",
        "messages_count_total": 1523,
        "reactions_given": 245,
        "reactions_received": 189,
        "voice_total_time_spent": 10,  # hours
    },
    {
        "discord_id": "234567890123456789",
        "roles": [Role.MEMBER, Role.PLAYER, Role.REFEREE],
        "has_server_tag": True,
        "dm_opt_in": False,
        "joined_at": "2023-06-20T14:00:00Z",
        "last_active_at": "2026-01-07T09:15:00Z",
        "messages_count_total": 4521,
        "reactions_given": 892,
        "reactions_received": 1245,
        "voice_total_time_spent": 40,
    },
    {
        "discord_id": "345678901234567890",
        "roles": [Role.MEMBER],
        "has_server_tag": False,
        "dm_opt_in": True,
        "joined_at": "2025-11-01T08:00:00Z",
        "last_active_at": "2026-01-06T22:30:00Z",
        "messages_count_total": 87,
        "reactions_given": 23,
        "reactions_received": 15,
        "voice_total_time_spent": 1,
    },
    {
        "discord_id": "456789012345678901",
        "roles": [Role.MEMBER, Role.PLAYER],
        "has_server_tag": True,
        "dm_opt_in": True,
        "joined_at": "2025-10-05T12:00:00Z",
        "last_active_at": "2026-01-08T21:10:00Z",
        "messages_count_total": 12050,
        "reactions_given": 980,
        "reactions_received": 1120,
        "voice_total_time_spent": 750,
    },
    {
        "discord_id": "567890123456789012",
        "roles": [Role.MEMBER],
        "has_server_tag": False,
        "dm_opt_in": False,
        "joined_at": "2025-12-01T09:30:00Z",
        "last_active_at": "2026-01-04T18:00:00Z",
        "messages_count_total": 15,
        "reactions_given": 2,
        "reactions_received": 1,
        "voice_total_time_spent": 0,
    },
    {
        "discord_id": "678901234567890123",
        "roles": [Role.MEMBER, Role.PLAYER, Role.REFEREE],
        "has_server_tag": True,
        "dm_opt_in": True,
        "joined_at": "2025-09-10T17:00:00Z",
        "last_active_at": "2026-01-07T20:45:00Z",
        "messages_count_total": 48752,
        "reactions_given": 1350,
        "reactions_received": 2210,
        "voice_total_time_spent": 1500,
    },
    {
        "discord_id": "789012345678901234",
        "roles": [Role.MEMBER, Role.PLAYER],
        "has_server_tag": True,
        "dm_opt_in": False,
        "joined_at": "2025-11-14T11:15:00Z",
        "last_active_at": "2026-01-03T13:20:00Z",
        "messages_count_total": 2330,
        "reactions_given": 155,
        "reactions_received": 220,
        "voice_total_time_spent": 50,
    },
    {
        "discord_id": "890123456789012345",
        "roles": [Role.MEMBER, Role.REFEREE],
        "has_server_tag": True,
        "dm_opt_in": True,
        "joined_at": "2025-09-25T08:45:00Z",
        "last_active_at": "2026-01-06T09:00:00Z",
        "messages_count_total": 8050,
        "reactions_given": 540,
        "reactions_received": 760,
        "voice_total_time_spent": 283,
    },
]

DEMO_CHARACTERS = [
    {
        "name": "Thorin Ironforge",
        "status": CharacterRole.ACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/12345678",
        "character_thread_link": "https://discord.com/channels/123/456",
        "token_link": "https://i.imgur.com/token1.png",
        "art_link": "https://i.imgur.com/thorin.png",
        "description": "A gruff dwarf fighter with a heart of gold and a beard of steel.",
        "notes": "Favorite weapon: battleaxe",
        "tags": ["dwarf", "fighter", "tank"],
        "quests_played": 12,
        "summaries_written": 8,
    },
    {
        "name": "Elara Moonshadow",
        "status": CharacterRole.ACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/23456789",
        "character_thread_link": "https://discord.com/channels/123/457",
        "token_link": "https://i.imgur.com/token2.png",
        "art_link": "https://i.imgur.com/elara.png",
        "description": "An elven wizard who speaks to the stars and communes with ancient spirits.",
        "notes": "Specializes in divination magic",
        "tags": ["elf", "wizard", "diviner"],
        "quests_played": 8,
        "summaries_written": 5,
    },
    {
        "name": "Grimm Blackwood",
        "status": CharacterRole.ACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/34567890",
        "character_thread_link": "https://discord.com/channels/123/458",
        "token_link": "https://i.imgur.com/token3.png",
        "art_link": "https://i.imgur.com/grimm.png",
        "description": "A tiefling warlock bound to a mysterious patron from the Far Realm.",
        "notes": "Speaks in riddles when nervous",
        "tags": ["tiefling", "warlock", "eldritch"],
        "quests_played": 15,
        "summaries_written": 10,
    },
    {
        "name": "Sera Brightblade",
        "status": CharacterRole.ACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/45678901",
        "character_thread_link": "https://discord.com/channels/123/459",
        "token_link": "https://i.imgur.com/token4.png",
        "art_link": "https://i.imgur.com/sera.png",
        "description": "A human paladin sworn to protect the innocent and vanquish evil.",
        "notes": "Always carries her grandmother's holy symbol",
        "tags": ["human", "paladin", "devotion"],
        "quests_played": 20,
        "summaries_written": 15,
    },
    {
        "name": "Zephyr Quickfingers",
        "status": CharacterRole.INACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/56789012",
        "character_thread_link": "https://discord.com/channels/123/460",
        "token_link": "https://i.imgur.com/token5.png",
        "art_link": "https://i.imgur.com/zephyr.png",
        "description": "A halfling rogue with a talent for getting into (and out of) trouble.",
        "notes": "Retired after the Heist of House Blackwood",
        "tags": ["halfling", "rogue", "retired"],
        "quests_played": 25,
        "summaries_written": 12,
    },
    {
        "name": "Kira Stormwind",
        "status": CharacterRole.ACTIVE,
        "ddb_link": "https://www.dndbeyond.com/characters/67890123",
        "character_thread_link": "https://discord.com/channels/123/461",
        "token_link": "https://i.imgur.com/token6.png",
        "art_link": "https://i.imgur.com/kira.png",
        "description": "A dragonborn sorcerer whose bloodline traces back to an ancient storm dragon.",
        "notes": "Has a fear of enclosed spaces",
        "tags": ["dragonborn", "sorcerer", "storm"],
        "quests_played": 6,
        "summaries_written": 4,
    },
]

DEMO_QUESTS = [
    {
        "title": "The Lost Mines of Phandelver",
        "description": "Adventurers are hired to escort a wagon of supplies to the mining town of Phandalin. But danger lurks on the road, and the fate of the mines hangs in the balance.",
        "status": QuestStatus.COMPLETED,
        "starting_at": "2025-12-15T18:00:00Z",
        "duration_hours": 4,
        "image_url": "https://i.imgur.com/quest1.jpg",
        "signups_count": 4,
    },
    {
        "title": "Dragon of Icespire Peak",
        "description": "A white dragon has descended upon the region, and the town of Phandalin needs heroes to drive it away before winter claims everything.",
        "status": QuestStatus.ANNOUNCED,
        "starting_at": "2026-01-20T19:00:00Z",
        "duration_hours": 3,
        "image_url": "https://i.imgur.com/quest2.jpg",
        "signups_count": 3,
    },
    {
        "title": "The Sunless Citadel",
        "description": "Delve into the depths of an ancient fortress to rescue the missing adventurers and uncover the source of the magical fruit that grows in darkness.",
        "status": QuestStatus.SIGNUP_CLOSED,
        "starting_at": "2026-01-15T20:00:00Z",
        "duration_hours": 5,
        "image_url": "https://i.imgur.com/quest3.jpg",
        "signups_count": 5,
    },
    {
        "title": "Curse of Strahd - Session 12",
        "description": "The party ventures deeper into Castle Ravenloft, seeking the artifacts needed to defeat the vampire lord.",
        "status": QuestStatus.DRAFT,
        "starting_at": "2026-01-25T18:00:00Z",
        "duration_hours": 4,
        "image_url": None,
        "signups_count": 0,
    },
    {
        "title": "Wild Beyond the Witchlight",
        "description": "A whimsical adventure awaits as the carnival comes to town. But beneath the wonder lies a dark secret.",
        "status": QuestStatus.COMPLETED,
        "starting_at": "2025-11-20T17:00:00Z",
        "duration_hours": 3,
        "image_url": "https://i.imgur.com/quest5.jpg",
        "signups_count": 4,
    },
    {
        "title": "Tomb of Annihilation",
        "description": "A death curse grips the land. Journey to the jungles of Chult to find and destroy the Soulmonger.",
        "status": QuestStatus.CANCELLED,
        "starting_at": "2025-10-15T19:00:00Z",
        "duration_hours": 6,
        "image_url": "https://i.imgur.com/quest6.jpg",
        "signups_count": 2,
    },
]

DEMO_SUMMARIES = [
    {
        "kind": SummaryKind.PLAYER,
        "title": "The Goblin Ambush",
        "description": "Our party was ambushed by goblins on the Triboar Trail. After a fierce battle, we tracked them back to their hideout in Cragmaw Cave. Thorin's axe cleaved through three goblins, while Elara's magic missiles lit up the darkness.",
    },
    {
        "kind": SummaryKind.REFEREE,
        "title": "Session 1 - DM Notes",
        "description": "The players handled the goblin ambush well. They showed good teamwork and tactical thinking. Grimm's use of Eldritch Blast to cover the retreat was particularly clever. Next session will begin in Cragmaw Cave.",
    },
    {
        "kind": SummaryKind.PLAYER,
        "title": "Clearing Cragmaw Cave",
        "description": "We fought our way through the goblin lair, freeing Sildar Hallwinter. The goblin boss Klarg nearly killed Zephyr, but Sera's healing saved the day. We found evidence pointing to Castle Cragmaw.",
    },
    {
        "kind": SummaryKind.PLAYER,
        "title": "The Dragon's First Strike",
        "description": "Cryovain attacked while we were traveling to the Shrine of Savras. The party barely escaped with their lives. Kira's lightning breath actually hurt the dragon - a glimmer of hope!",
    },
    {
        "kind": SummaryKind.REFEREE,
        "title": "Dragon Attack - DM Retrospective",
        "description": "The random encounter with Cryovain went perfectly. The players are now properly terrified and motivated. Their resource management will be tested as they prepare for the final confrontation.",
    },
]

DEMO_LOOKUPS = [
    {
        "name": "PHB",
        "url": "https://www.dndbeyond.com/sources/phb",
        "description": "Player's Handbook - Core rulebook for D&D 5th Edition",
    },
    {
        "name": "DMG",
        "url": "https://www.dndbeyond.com/sources/dmg",
        "description": "Dungeon Master's Guide - Essential guide for DMs",
    },
    {
        "name": "MM",
        "url": "https://www.dndbeyond.com/sources/mm",
        "description": "Monster Manual - Bestiary of creatures for D&D",
    },
    {
        "name": "XGE",
        "url": "https://www.dndbeyond.com/sources/xgte",
        "description": "Xanathar's Guide to Everything - Player and DM options",
    },
    {
        "name": "TCE",
        "url": "https://www.dndbeyond.com/sources/tcoe",
        "description": "Tasha's Cauldron of Everything - Additional character options",
    },
    {
        "name": "Server Rules",
        "url": "https://example.com/server-rules",
        "description": "Our server's house rules and guidelines",
    },
    {
        "name": "Character Creation",
        "url": "https://example.com/chargen",
        "description": "Guide to creating a character for our server",
    },
]


# ============================================================================
# Seeding Functions
# ============================================================================

async def seed_users(users_repo: UsersRepoPostgres) -> dict[int, UserID]:
    """Seed demo users and return mapping of index to UserID."""
    print("Seeding users...")
    user_ids = {}
    
    for i, user_data in enumerate(DEMO_USERS):
        user_id_str = await users_repo.next_id(DEMO_GUILD_ID)
        user_id = UserID.parse(user_id_str)
        
        player = None
        referee = None
        
        if Role.PLAYER in user_data["roles"]:
            player = Player(characters=[])
        
        if Role.REFEREE in user_data["roles"]:
            referee = Referee()
        
        user = User(
            user_id=user_id,
            guild_id=DEMO_GUILD_ID,
            discord_id=user_data["discord_id"],
            roles=user_data["roles"],
            has_server_tag=user_data["has_server_tag"],
            dm_opt_in=user_data["dm_opt_in"],
            joined_at=parse_datetime(user_data["joined_at"]),
            last_active_at=parse_datetime(user_data["last_active_at"]),
            messages_count_total=user_data["messages_count_total"],
            reactions_given=user_data["reactions_given"],
            reactions_received=user_data["reactions_received"],
            voice_total_time_spent=user_data["voice_total_time_spent"],
            player=player,
            referee=referee,
        )
        
        await users_repo.upsert(DEMO_GUILD_ID, user)
        user_ids[i] = user_id
        print(f"  Created user {user_id}")
    
    return user_ids


async def seed_characters(
    characters_repo: CharactersRepoPostgres,
    user_ids: dict[int, UserID],
) -> dict[int, CharacterID]:
    """Seed demo characters and return mapping of index to CharacterID."""
    print("Seeding characters...")
    character_ids = {}
    
    # Assign characters to users who are players
    player_user_indices = [i for i, data in enumerate(DEMO_USERS) if Role.PLAYER in data["roles"]]
    
    for i, char_data in enumerate(DEMO_CHARACTERS):
        char_id_str = await characters_repo.next_id(DEMO_GUILD_ID)
        char_id = CharacterID.parse(char_id_str)
        
        # Assign to a player user (round-robin)
        owner_index = player_user_indices[i % len(player_user_indices)]
        owner_id = user_ids[owner_index]
        
        character = Character(
            character_id=str(char_id),
            guild_id=DEMO_GUILD_ID,
            owner_id=owner_id,
            name=char_data["name"],
            status=char_data["status"],
            ddb_link=char_data["ddb_link"],
            character_thread_link=char_data["character_thread_link"],
            token_link=char_data["token_link"],
            art_link=char_data["art_link"],
            description=char_data["description"],
            notes=char_data["notes"],
            tags=char_data["tags"],
            quests_played=char_data["quests_played"],
            summaries_written=char_data["summaries_written"],
            created_at=datetime.now(timezone.utc) - timedelta(days=90 - i * 10),
            last_played_at=datetime.now(timezone.utc) - timedelta(days=i * 5),
        )
        
        await characters_repo.upsert(DEMO_GUILD_ID, character)
        character_ids[i] = char_id
        print(f"  Created character {char_id} ({char_data['name']})")
    
    return character_ids


async def seed_quests(
    quests_repo: QuestsRepoPostgres,
    user_ids: dict[int, UserID],
    character_ids: dict[int, CharacterID],
) -> dict[int, QuestID]:
    """Seed demo quests and return mapping of index to QuestID."""
    print("Seeding quests...")
    quest_ids = {}
    
    # Get referee user indices
    referee_indices = [i for i, data in enumerate(DEMO_USERS) if Role.REFEREE in data["roles"]]
    
    for i, quest_data in enumerate(DEMO_QUESTS):
        quest_id_str = await quests_repo.next_id(DEMO_GUILD_ID)
        quest_id = QuestID.parse(quest_id_str)
        
        # Assign to a referee (round-robin)
        referee_index = referee_indices[i % len(referee_indices)]
        referee_id = user_ids[referee_index]
        
        # Create signups
        signups = []
        if quest_data["signups_count"] > 0:
            # Get player user indices (excluding the referee)
            player_indices = [
                idx for idx, data in enumerate(DEMO_USERS)
                if Role.PLAYER in data["roles"] and idx != referee_index
            ]
            
            for j in range(min(quest_data["signups_count"], len(player_indices))):
                player_idx = player_indices[j]
                char_idx = j % len(character_ids)
                signups.append(PlayerSignUp(
                    user_id=user_ids[player_idx],
                    character_id=character_ids[char_idx],
                    signed_up_at=parse_datetime(quest_data["starting_at"]) - timedelta(days=j + 1),
                    status=PlayerStatus.SELECTED if j < 4 else PlayerStatus.APPLIED,
                ))
        
        quest = Quest(
            quest_id=quest_id,
            guild_id=DEMO_GUILD_ID,
            referee_id=referee_id,
            raw=quest_data["description"],
            title=quest_data["title"],
            description=quest_data["description"],
            starting_at=parse_datetime(quest_data["starting_at"]),
            duration=timedelta(hours=quest_data["duration_hours"]),
            image_url=quest_data["image_url"],
            status=quest_data["status"],
            announce_at=parse_datetime(quest_data["starting_at"]) - timedelta(days=7),
            signups=signups,
        )
        
        if quest_data["status"] == QuestStatus.COMPLETED:
            quest.started_at = parse_datetime(quest_data["starting_at"])
            quest.ended_at = quest.started_at + timedelta(hours=quest_data["duration_hours"])
        
        await quests_repo.upsert(DEMO_GUILD_ID, quest)
        quest_ids[i] = quest_id
        print(f"  Created quest {quest_id} ({quest_data['title']})")
    
    return quest_ids


async def seed_summaries(
    summaries_repo: SummariesRepoPostgres,
    user_ids: dict[int, UserID],
    character_ids: dict[int, CharacterID],
    quest_ids: dict[int, QuestID],
) -> None:
    """Seed demo summaries."""
    print("Seeding summaries...")
    
    # Get player and referee indices
    player_indices = [i for i, data in enumerate(DEMO_USERS) if Role.PLAYER in data["roles"]]
    referee_indices = [i for i, data in enumerate(DEMO_USERS) if Role.REFEREE in data["roles"]]
    
    for i, summary_data in enumerate(DEMO_SUMMARIES):
        summary_id_str = await summaries_repo.next_id(DEMO_GUILD_ID)
        summary_id = SummaryID.parse(summary_id_str)
        
        # Assign author based on kind
        if summary_data["kind"] == SummaryKind.PLAYER:
            author_index = player_indices[i % len(player_indices)]
            char_index = i % len(character_ids)
            character_id = character_ids[char_index]
        else:
            author_index = referee_indices[i % len(referee_indices)]
            character_id = None
        
        author_id = user_ids[author_index]
        quest_id = quest_ids[i % len(quest_ids)]
        
        # For player summaries, we need at least one character
        characters_list = [character_ids[i % len(character_ids)]] if summary_data["kind"] == SummaryKind.PLAYER else [character_ids[0]]
        
        summary = QuestSummary(
            summary_id=summary_id,
            guild_id=DEMO_GUILD_ID,
            kind=summary_data["kind"],
            author_id=author_id,
            character_id=character_id,
            quest_id=quest_id,
            raw=summary_data["description"],
            title=summary_data["title"],
            description=summary_data["description"],
            created_on=datetime.now(timezone.utc) - timedelta(days=30 - i * 5),
            characters=characters_list,
            players=[author_id],
            status=SummaryStatus.POSTED,
        )
        
        await summaries_repo.upsert(DEMO_GUILD_ID, summary)
        print(f"  Created summary {summary_id} ({summary_data['title']})")


async def seed_lookups(lookup_repo: LookupRepoPostgres) -> None:
    """Seed demo lookup entries."""
    print("Seeding lookups...")
    
    for i, lookup_data in enumerate(DEMO_LOOKUPS):
        entry = LookupEntry(
            guild_id=DEMO_GUILD_ID,
            name=lookup_data["name"],
            url=lookup_data["url"],
            description=lookup_data["description"],
            created_by=123456789012345678,  # Demo discord ID
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
        )
        
        await lookup_repo.upsert(entry)
        print(f"  Created lookup '{lookup_data['name']}'")


async def main():
    """Main seed function."""
    print("=" * 60)
    print("Nonagon Demo Data Seeder")
    print(f"Target Guild ID: {DEMO_GUILD_ID}")
    print("=" * 60)
    print()
    
    # Initialize database
    print("Initializing database connection...")
    await init_db()
    
    try:
        # Initialize repositories
        users_repo = UsersRepoPostgres()
        characters_repo = CharactersRepoPostgres()
        quests_repo = QuestsRepoPostgres()
        summaries_repo = SummariesRepoPostgres()
        lookup_repo = LookupRepoPostgres()
        
        # Seed data in order (respecting foreign key relationships)
        user_ids = await seed_users(users_repo)
        character_ids = await seed_characters(characters_repo, user_ids)
        quest_ids = await seed_quests(quests_repo, user_ids, character_ids)
        await seed_summaries(summaries_repo, user_ids, character_ids, quest_ids)
        await seed_lookups(lookup_repo)
        
        print()
        print("=" * 60)
        print("Seeding complete!")
        print(f"  Users: {len(user_ids)}")
        print(f"  Characters: {len(character_ids)}")
        print(f"  Quests: {len(quest_ids)}")
        print(f"  Summaries: {len(DEMO_SUMMARIES)}")
        print(f"  Lookups: {len(DEMO_LOOKUPS)}")
        print("=" * 60)
        
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
