/* AUTO-GENERATED - DO NOT EDIT */
/* Generated from shared/schemas/enums.schema.json */
/* Regenerate with: ./scripts/generate-types.sh */

/**
 * User roles within a guild
 */
export type Role = 'MEMBER' | 'PLAYER' | 'REFEREE';

/**
 * Quest lifecycle states
 */
export type QuestState = 'DRAFT' | 'OPEN' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

/**
 * Character availability status
 */
export type CharacterStatus = 'ACTIVE' | 'RETIRED';

/**
 * Player signup status for a quest
 */
export type SignUpStatus = 'PENDING' | 'ACCEPTED';

/**
 * Quest summary publication status
 */
export type SummaryStatus = 'DRAFT' | 'PUBLISHED';

/**
 * Type of summary author
 */
export type AuthorType = 'PLAYER' | 'REFEREE';
