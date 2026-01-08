/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/summary.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

import type { SummaryID, UserID, CharacterID, QuestID, DiscordSnowflake, ISODateTime, NullableDateTime, NullableString } from './common';
import type { AuthorType, SummaryStatus } from './enums';

/**
 * Quest summary/write-up entity
 */
export interface QuestSummary {
  /** Unique summary identifier */
  summary_id: SummaryID;
  /** Discord guild this summary belongs to */
  guild_id: DiscordSnowflake;
  /** Whether author is player or referee */
  author_type: AuthorType;
  /** User ID of the author */
  author_id?: UserID | null;
  /** Character ID if author is a player */
  character_id?: CharacterID | null;
  /** Related quest ID */
  quest_id?: QuestID | null;
  /** Summary title */
  title?: NullableString;
  /** Summary content (markdown) */
  content?: NullableString;
  /** Creation timestamp */
  created_at: ISODateTime;
  /** Last edit timestamp */
  edited_at?: NullableDateTime;
  /** Participating player user IDs */
  players: UserID[];
  /** Participating character IDs */
  characters: CharacterID[];
  /** Related quest IDs */
  linked_quests: QuestID[];
  /** Related summary IDs */
  linked_summaries: SummaryID[];
  /** Discord channel ID */
  channel_id?: DiscordSnowflake | null;
  /** Discord message ID */
  message_id?: DiscordSnowflake | null;
  /** Discord thread ID */
  thread_id?: DiscordSnowflake | null;
  /** Publication status */
  status: SummaryStatus;
}
