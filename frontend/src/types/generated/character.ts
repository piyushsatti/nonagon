/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/character.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

import type { CharacterID, UserID, QuestID, SummaryID, DiscordSnowflake, NullableDateTime, NullableString, URL } from './common';
import type { CharacterStatus } from './enums';

/**
 * Player character entity
 */
export interface Character {
  /** Unique character identifier */
  character_id: CharacterID;
  /** User ID of the owning player */
  owner_id: UserID;
  /** Discord guild this character belongs to */
  guild_id?: DiscordSnowflake | null;
  /** Character name */
  name: string;
  /** D&D Beyond character sheet URL */
  sheet_url: URL;
  /** Character thread URL */
  thread_url: URL;
  /** Character token image URL */
  token_url: URL;
  /** Character art URL */
  art_url: URL;
  /** Character status (ACTIVE or RETIRED) */
  status: CharacterStatus;
  /** Discord channel ID */
  channel_id?: DiscordSnowflake | null;
  /** Discord message ID */
  message_id?: DiscordSnowflake | null;
  /** Discord thread ID */
  thread_id?: DiscordSnowflake | null;
  /** Character creation timestamp */
  created_at?: NullableDateTime;
  /** Last quest played timestamp */
  last_played_at?: NullableDateTime;
  /** Number of quests played */
  quests_played_count?: number;
  /** Number of summaries written */
  summaries_count?: number;
  /** Character description/backstory */
  description?: NullableString;
  /** Private notes (staff-only) */
  notes?: NullableString;
  /** Custom tags */
  tags?: string[];
  /** Other characters played with */
  played_with?: CharacterID[];
  /** Quest history */
  played_in?: QuestID[];
  /** Summaries mentioning this character */
  mentioned_in?: SummaryID[];
}
