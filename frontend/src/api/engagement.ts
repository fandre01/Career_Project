import { api } from './client';
import type { PaginatedComments, Comment, ViewStats } from '../types/engagement';

export function fetchComments(page = 1, pageSize = 20): Promise<PaginatedComments> {
  return api.get(`/engagement/comments?page=${page}&page_size=${pageSize}`);
}

export async function postComment(name: string, message: string): Promise<Comment> {
  const res = await fetch('/api/engagement/comments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, message }),
  });
  if (res.status === 429) {
    throw new Error('RATE_LIMITED');
  }
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export function trackPageView(page = '/'): Promise<unknown> {
  return api.post('/engagement/views/track', { page });
}

export function fetchViewStats(): Promise<ViewStats> {
  return api.get('/engagement/views/stats');
}
