import { GraphQLClient, gql } from 'graphql-request';

const GRAPHQL_ENDPOINT = process.env.API_URL 
  ? `${process.env.API_URL}/graphql`
  : 'http://localhost:8000/graphql';

export const graphqlClient = new GraphQLClient(GRAPHQL_ENDPOINT);

// Query fragments for reusable fields
const USER_FIELDS = `
  userId
  guildId
  discordId
  roles
  hasServerTag
  dmOptIn
  joinedAt
  lastActiveAt
  messagesCountTotal
  reactionsGiven
  reactionsReceived
  voiceTotalTimeSpent
`;

const QUEST_FIELDS = `
  questId
  guildId
  refereeId
  channelId
  messageId
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
    signedUpAt
    selected
  }
`;

const CHARACTER_FIELDS = `
  characterId
  guildId
  ownerId
  name
  status
  ddbLink
  characterThreadLink
  tokenLink
  artLink
  description
  notes
  tags
  createdAt
  lastPlayedAt
  questsPlayed
  summariesWritten
`;

const SUMMARY_FIELDS = `
  summaryId
  guildId
  kind
  authorId
  characterId
  questId
  title
  description
  createdOn
  lastEditedAt
  status
`;

const LOOKUP_FIELDS = `
  name
  guildId
  kind
  value
  sourceUrl
  createdAt
  updatedAt
`;

// Queries
export const GET_USER = gql`
  query GetUser($guildId: Int!, $userId: String!) {
    user(guildId: $guildId, userId: $userId) {
      ${USER_FIELDS}
    }
  }
`;

export const GET_USER_BY_DISCORD = gql`
  query GetUserByDiscord($guildId: Int!, $discordId: String!) {
    userByDiscord(guildId: $guildId, discordId: $discordId) {
      ${USER_FIELDS}
    }
  }
`;

export const GET_QUEST = gql`
  query GetQuest($guildId: Int!, $questId: String!) {
    quest(guildId: $guildId, questId: $questId) {
      ${QUEST_FIELDS}
    }
  }
`;

export const GET_CHARACTER = gql`
  query GetCharacter($guildId: Int!, $characterId: String!) {
    character(guildId: $guildId, characterId: $characterId) {
      ${CHARACTER_FIELDS}
    }
  }
`;

export const GET_SUMMARY = gql`
  query GetSummary($guildId: Int!, $summaryId: String!) {
    summary(guildId: $guildId, summaryId: $summaryId) {
      ${SUMMARY_FIELDS}
    }
  }
`;

export const GET_ALL_LOOKUPS = gql`
  query GetAllLookups($guildId: Int!) {
    allLookups(guildId: $guildId) {
      ${LOOKUP_FIELDS}
    }
  }
`;

export const SEARCH_LOOKUPS = gql`
  query SearchLookups($guildId: Int!, $partial: String!) {
    lookupSearch(guildId: $guildId, partial: $partial) {
      ${LOOKUP_FIELDS}
    }
  }
`;

// API functions
export async function fetchUser(guildId, userId) {
  const data = await graphqlClient.request(GET_USER, { guildId: parseInt(guildId), userId });
  return data.user;
}

export async function fetchUserByDiscord(guildId, discordId) {
  const data = await graphqlClient.request(GET_USER_BY_DISCORD, { guildId: parseInt(guildId), discordId });
  return data.userByDiscord;
}

export async function fetchQuest(guildId, questId) {
  const data = await graphqlClient.request(GET_QUEST, { guildId: parseInt(guildId), questId });
  return data.quest;
}

export async function fetchCharacter(guildId, characterId) {
  const data = await graphqlClient.request(GET_CHARACTER, { guildId: parseInt(guildId), characterId });
  return data.character;
}

export async function fetchSummary(guildId, summaryId) {
  const data = await graphqlClient.request(GET_SUMMARY, { guildId: parseInt(guildId), summaryId });
  return data.summary;
}

export async function fetchAllLookups(guildId) {
  const data = await graphqlClient.request(GET_ALL_LOOKUPS, { guildId: parseInt(guildId) });
  return data.allLookups;
}

export async function searchLookups(guildId, partial) {
  const data = await graphqlClient.request(SEARCH_LOOKUPS, { guildId: parseInt(guildId), partial });
  return data.lookupSearch;
}
