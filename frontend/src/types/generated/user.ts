/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/user.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

import type { CharacterID, QuestID, SummaryID, UserID, DiscordSnowflake, NullableDateTime } from './common';
import type { Role } from './enums';

/**
 * Statistics for playing with another character
 */
export interface PlayedWithStats {
  /** Number of times played together */
  frequency: number;
  /** Total hours played together */
  hours: number;
}

/**
 * Collaboration statistics with another user
 */
export interface CollabStats {
  /** Number of collaborations */
  frequency: number;
  /** Total hours collaborated */
  hours: number;
}

/**
 * Player profile embedded in User
 */
export interface Player {
  /** List of character IDs owned by player */
  characters: CharacterID[];
  /** When user became a player */
  became_player_at?: NullableDateTime;
  /** When first character was created */
  first_character_at?: NullableDateTime;
  /** Last play session timestamp */
  last_played_at?: NullableDateTime;
  /** Quest IDs applied to */
  quests_applied: QuestID[];
  /** Quest IDs completed */
  quests_played: QuestID[];
  /** Summary IDs authored as player */
  summaries_written: SummaryID[];
  /** Map of CharacterID to play statistics */
  played_with_character?: Record<string, PlayedWithStats>;
}

/**
 * Referee profile embedded in User
 */
export interface Referee {
  /** Quest IDs hosted as referee */
  quests_hosted: QuestID[];
  /** Summary IDs authored as referee */
  summaries_written: SummaryID[];
  /** First DM session timestamp */
  first_dm_at?: NullableDateTime;
  /** Last DM session timestamp */
  last_dm_at?: NullableDateTime;
  /** Map of UserID to collaboration statistics */
  collabed_with?: Record<string, CollabStats>;
  /** Map of UserID to times hosted for */
  hosted_for?: Record<string, number>;
}

/**
 * Main user entity
 */
export interface User {
  /** Unique user identifier */
  user_id: UserID;
  /** Discord guild this user belongs to */
  guild_id: DiscordSnowflake;
  /** Discord user snowflake ID */
  discord_id?: DiscordSnowflake | null;
  /** User roles */
  roles: Role[];
  /** Whether user has server tag */
  is_tagged?: boolean;
  /** Whether user allows DM notifications */
  allow_dm?: boolean;
  /** When user joined */
  joined_at?: NullableDateTime;
  /** Last activity timestamp */
  last_active_at?: NullableDateTime;
  /** Total messages sent */
  messages_count_total?: number;
  /** Messages sent this week */
  messages_count_week?: number;
  /** Total voice minutes */
  voice_minutes_total?: number;
  /** Total reactions given */
  reactions_count_total?: number;
  /** Whether user has player role */
  is_player: boolean;
  /** Whether user has referee role */
  is_referee: boolean;
  /** Player profile if user is a player */
  player?: Player | null;
  /** Referee profile if user is a referee */
  referee?: Referee | null;
}
