import { GraphQLClient, gql } from "graphql-request";
import { getAllDummyData } from "../data/dummy";

const GRAPHQL_ENDPOINT = process.env.API_URL
  ? `${process.env.API_URL}/graphql`
  : "http://localhost:8000/graphql";

export const graphqlClient = new GraphQLClient(GRAPHQL_ENDPOINT);

// Backend availability status
let backendStatusCallback = null;
let retryDelay = 1000; // Start with 1 second
const MAX_RETRY_DELAY = 30000; // Max 30 seconds

export function setBackendStatusCallback(callback) {
  backendStatusCallback = callback;
}

function notifyBackendStatus(isAvailable) {
  if (backendStatusCallback) {
    backendStatusCallback(isAvailable);
  }
}

// Exponential backoff retry wrapper
async function withRetry(requestFn, fallbackFn) {
  try {
    const result = await requestFn();
    // Success - reset retry delay
    retryDelay = 1000;
    notifyBackendStatus(true);
    return result;
  } catch (error) {
    console.warn(
      `Backend unavailable (will retry in ${
        retryDelay / 1000
      }s), using dummy data:`,
      error.message
    );
    notifyBackendStatus(false);

    // Schedule retry with exponential backoff
    setTimeout(() => {
      // Double the delay for next retry, capped at MAX_RETRY_DELAY
      retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY);
    }, retryDelay);

    return fallbackFn();
  }
}

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
  url
  description
  createdBy
  createdAt
  updatedBy
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

// Demo guild ID - maps "demo" to this numeric ID
export const DEMO_GUILD_ID = 99999;

export function resolveGuildId(guildId) {
  if (guildId === "demo") {
    return DEMO_GUILD_ID;
  }
  return parseInt(guildId);
}

// List queries
export const GET_USERS_BY_GUILD = gql`
  query GetUsersByGuild($guildId: Int!) {
    usersByGuild(guildId: $guildId) {
      ${USER_FIELDS}
    }
  }
`;

export const GET_CHARACTERS_BY_GUILD = gql`
  query GetCharactersByGuild($guildId: Int!) {
    charactersByGuild(guildId: $guildId) {
      ${CHARACTER_FIELDS}
    }
  }
`;

export const GET_SUMMARIES_BY_GUILD = gql`
  query GetSummariesByGuild($guildId: Int!) {
    summariesByGuild(guildId: $guildId) {
      ${SUMMARY_FIELDS}
    }
  }
`;

export const GET_RECENT_QUESTS = gql`
  query GetRecentQuests($guildId: Int!, $limit: Int) {
    recentQuests(guildId: $guildId, limit: $limit) {
      ${QUEST_FIELDS}
    }
  }
`;

export const GET_ACTIVITY_STATS = gql`
  query GetActivityStats($guildId: Int!) {
    activityStats(guildId: $guildId) {
      totalMessages
      totalReactions
      totalVoiceHours
      activeUsers
      totalQuests
      totalCharacters
      totalSummaries
      topContributors {
        userId
        discordId
        username
        messages
        reactions
        voiceHours
      }
    }
  }
`;

// API functions
export async function fetchUser(guildId, userId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_USER, {
          guildId: resolveGuildId(guildId),
          userId,
        })
        .then((data) => data.user),
    () => getAllDummyData().users.find((u) => u.userId === userId)
  );
}

export async function fetchUserByDiscord(guildId, discordId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_USER_BY_DISCORD, {
          guildId: resolveGuildId(guildId),
          discordId,
        })
        .then((data) => data.userByDiscord),
    () => getAllDummyData().users.find((u) => u.discordId === discordId)
  );
}

export async function fetchQuest(guildId, questId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_QUEST, {
          guildId: resolveGuildId(guildId),
          questId,
        })
        .then((data) => data.quest),
    () => getAllDummyData().quests.find((q) => q.questId === questId)
  );
}

export async function fetchCharacter(guildId, characterId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_CHARACTER, {
          guildId: resolveGuildId(guildId),
          characterId,
        })
        .then((data) => data.character),
    () =>
      getAllDummyData().characters.find((c) => c.characterId === characterId)
  );
}

export async function fetchSummary(guildId, summaryId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_SUMMARY, {
          guildId: resolveGuildId(guildId),
          summaryId,
        })
        .then((data) => data.summary),
    () => getAllDummyData().summaries.find((s) => s.summaryId === summaryId)
  );
}

export async function fetchAllLookups(guildId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_ALL_LOOKUPS, {
          guildId: resolveGuildId(guildId),
        })
        .then((data) => data.allLookups),
    () => getAllDummyData().lookups
  );
}

export async function searchLookups(guildId, partial) {
  return withRetry(
    () =>
      graphqlClient
        .request(SEARCH_LOOKUPS, {
          guildId: resolveGuildId(guildId),
          partial,
        })
        .then((data) => data.lookupSearch),
    () => {
      const lookups = getAllDummyData().lookups;
      return lookups.filter((l) =>
        l.name.toLowerCase().includes(partial.toLowerCase())
      );
    }
  );
}

// List fetch functions
export async function fetchUsersByGuild(guildId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_USERS_BY_GUILD, {
          guildId: resolveGuildId(guildId),
        })
        .then((data) => data.usersByGuild),
    () => getAllDummyData().users
  );
}

export async function fetchCharactersByGuild(guildId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_CHARACTERS_BY_GUILD, {
          guildId: resolveGuildId(guildId),
        })
        .then((data) => data.charactersByGuild),
    () => getAllDummyData().characters
  );
}

export async function fetchSummariesByGuild(guildId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_SUMMARIES_BY_GUILD, {
          guildId: resolveGuildId(guildId),
        })
        .then((data) => data.summariesByGuild),
    () => getAllDummyData().summaries
  );
}

export async function fetchRecentQuests(guildId, limit = 50) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_RECENT_QUESTS, {
          guildId: resolveGuildId(guildId),
          limit,
        })
        .then((data) => data.recentQuests),
    () => getAllDummyData().quests.slice(0, limit)
  );
}

export async function fetchActivityStats(guildId) {
  return withRetry(
    () =>
      graphqlClient
        .request(GET_ACTIVITY_STATS, {
          guildId: resolveGuildId(guildId),
        })
        .then((data) => data.activityStats),
    () => {
      const dummyData = getAllDummyData();

      // Compute stats from dummy data
      const totalMessages = dummyData.users.reduce(
        (sum, u) => sum + (u.messagesCountTotal || 0),
        0
      );
      const totalReactions = dummyData.users.reduce(
        (sum, u) => sum + (u.reactionsGiven || 0) + (u.reactionsReceived || 0),
        0
      );
      const totalVoiceHours = Math.round(
        dummyData.users.reduce(
          (sum, u) => sum + (u.voiceTotalTimeSpent || 0),
          0
        ) / 3600
      );
      const activeUsers = dummyData.users.filter(
        (u) =>
          u.lastActiveAt &&
          new Date(u.lastActiveAt) >
            new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      ).length;

      // Top contributors
      const topContributors = dummyData.users
        .map((u) => ({
          userId: u.userId,
          discordId: u.discordId,
          username: `User${u.userId.slice(-3)}`,
          messages: u.messagesCountTotal || 0,
          reactions: (u.reactionsGiven || 0) + (u.reactionsReceived || 0),
          voiceHours: Math.round((u.voiceTotalTimeSpent || 0) / 3600),
        }))
        .sort((a, b) => b.messages - a.messages)
        .slice(0, 5);

      return {
        totalMessages,
        totalReactions,
        totalVoiceHours,
        activeUsers,
        totalQuests: dummyData.quests.length,
        totalCharacters: dummyData.characters.length,
        totalSummaries: dummyData.summaries.length,
        topContributors,
      };
    }
  );
}
