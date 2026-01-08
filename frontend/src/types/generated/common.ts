/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/common.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

/**
 * User identifier (postal format USERH3X1T7 or legacy USER123)
 */
export type UserID = string;

/**
 * Quest identifier (postal format QUESH3X1T7 or legacy QUES123)
 */
export type QuestID = string;

/**
 * Character identifier (postal format CHARH3X1T7 or legacy CHAR123)
 */
export type CharacterID = string;

/**
 * Summary identifier (postal format SUMMH3X1T7 or legacy SUMM123)
 */
export type SummaryID = string;

/**
 * Discord snowflake ID (64-bit integer)
 */
export type DiscordSnowflake = number;

/**
 * ISO 8601 datetime string
 */
export type ISODateTime = string;

/**
 * ISO 8601 datetime string or null
 */
export type NullableDateTime = string | null;

/**
 * Valid URL string
 */
export type URL = string;

/**
 * Valid URL string or null
 */
export type NullableURL = string | null;

export type NullableString = string | null;

export type NullableInteger = number | null;
