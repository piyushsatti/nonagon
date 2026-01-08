/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/quest.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

import type { QuestID, UserID, CharacterID, SummaryID, DiscordSnowflake, NullableDateTime, NullableString, NullableURL } from './common';
import type { QuestState, SignUpStatus } from './enums';

/**
 * Player signup for a quest
 */
export interface PlayerSignUp {
  /** User signing up */
  user_id: UserID;
  /** Character for the quest */
  character_id: CharacterID;
  /** Signup status */
  status: SignUpStatus;
}

/**
 * Main quest entity
 */
export interface Quest {
  /** Unique quest identifier */
  quest_id: QuestID;
  /** Discord guild this quest belongs to */
  guild_id: DiscordSnowflake;
  /** User ID of the hosting referee */
  referee_id: UserID;
  /** Discord channel for the quest */
  channel_id?: DiscordSnowflake | null;
  /** Discord message ID for quest embed */
  message_id?: DiscordSnowflake | null;
  /** Quest title */
  title?: NullableString;
  /** Quest description */
  description?: NullableString;
  /** Scheduled start time */
  scheduled_start?: NullableDateTime;
  /** Expected duration in hours */
  duration_hours?: number | null;
  /** Cover image URL */
  image_url?: NullableURL;
  /** Related quest IDs */
  linked_quests: QuestID[];
  /** Related summary IDs */
  linked_summaries: SummaryID[];
  /** Current lifecycle state */
  state: QuestState;
  /** When quest was opened for signups */
  open_at?: NullableDateTime;
  /** When quest actually started */
  started_at?: NullableDateTime;
  /** When quest ended */
  ended_at?: NullableDateTime;
  /** List of player signups */
  signups: PlayerSignUp[];
  /** Total number of signups */
  signup_count?: number;
  /** Number of accepted signups */
  accepted_count?: number;
}
