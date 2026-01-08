/**
 * API client for Nonagon backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body?: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, body);
  }

  return response.json();
}

// Re-export types for convenience
export type { User, Player, Referee } from '@/types/generated/user';
export type { Quest, PlayerSignUp } from '@/types/generated/quest';
export type { Character } from '@/types/generated/character';
export type { QuestSummary } from '@/types/generated/summary';

import type { User } from '@/types/generated/user';
import type { Quest } from '@/types/generated/quest';
import type { Character } from '@/types/generated/character';
import type { QuestSummary } from '@/types/generated/summary';

/**
 * User API endpoints
 */
export const usersApi = {
  getAll: (guildId: number) => 
    fetchApi<User[]>(`/v1/guilds/${guildId}/users`),
  
  getById: (guildId: number, userId: string) => 
    fetchApi<User>(`/v1/guilds/${guildId}/users/${userId}`),
  
  create: (guildId: number, data: Partial<User>) => 
    fetchApi<User>(`/v1/guilds/${guildId}/users`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (guildId: number, userId: string, data: Partial<User>) => 
    fetchApi<User>(`/v1/guilds/${guildId}/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

/**
 * Quest API endpoints
 */
export const questsApi = {
  getAll: (guildId: number) => 
    fetchApi<Quest[]>(`/v1/guilds/${guildId}/quests`),
  
  getById: (guildId: number, questId: string) => 
    fetchApi<Quest>(`/v1/guilds/${guildId}/quests/${questId}`),
  
  create: (guildId: number, data: Partial<Quest>) => 
    fetchApi<Quest>(`/v1/guilds/${guildId}/quests`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (guildId: number, questId: string, data: Partial<Quest>) => 
    fetchApi<Quest>(`/v1/guilds/${guildId}/quests/${questId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

/**
 * Character API endpoints
 */
export const charactersApi = {
  getAll: (guildId: number) => 
    fetchApi<Character[]>(`/v1/guilds/${guildId}/characters`),
  
  getById: (guildId: number, characterId: string) => 
    fetchApi<Character>(`/v1/guilds/${guildId}/characters/${characterId}`),
  
  create: (guildId: number, data: Partial<Character>) => 
    fetchApi<Character>(`/v1/guilds/${guildId}/characters`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (guildId: number, characterId: string, data: Partial<Character>) => 
    fetchApi<Character>(`/v1/guilds/${guildId}/characters/${characterId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

/**
 * Summary API endpoints
 */
export const summariesApi = {
  getAll: (guildId: number) => 
    fetchApi<QuestSummary[]>(`/v1/guilds/${guildId}/summaries`),
  
  getById: (guildId: number, summaryId: string) => 
    fetchApi<QuestSummary>(`/v1/guilds/${guildId}/summaries/${summaryId}`),
  
  create: (guildId: number, data: Partial<QuestSummary>) => 
    fetchApi<QuestSummary>(`/v1/guilds/${guildId}/summaries`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (guildId: number, summaryId: string, data: Partial<QuestSummary>) => 
    fetchApi<QuestSummary>(`/v1/guilds/${guildId}/summaries/${summaryId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

/**
 * Health check
 */
export const healthApi = {
  check: () => fetchApi<{ status: string }>('/healthz'),
};
