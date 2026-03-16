import { api } from './client';
import type {
  PaginatedCareers,
  CareerDetail,
  CareerListItem,
  CareerRiskItem,
  IndustryBreakdown,
  TimelineItem,
  PlatformStats,
  CareerDNAResponse,
} from '../types/career';

interface CareerFilters {
  page?: number;
  page_size?: number;
  category?: string;
  salary_min?: number;
  salary_max?: number;
  risk_level?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

export function fetchCareers(filters: CareerFilters = {}): Promise<PaginatedCareers> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      params.set(key, String(value));
    }
  });
  return api.get(`/careers?${params}`);
}

export function fetchCareer(id: number): Promise<CareerDetail> {
  return api.get(`/careers/${id}`);
}

export function searchCareers(q: string, limit = 10): Promise<CareerListItem[]> {
  return api.get(`/careers/search?q=${encodeURIComponent(q)}&limit=${limit}`);
}

export function fetchCategories(): Promise<{ name: string; count: number }[]> {
  return api.get('/careers/categories');
}

export function fetchTopRisk(limit = 20): Promise<CareerRiskItem[]> {
  return api.get(`/predictions/top-risk?limit=${limit}`);
}

export function fetchTopSafe(limit = 20): Promise<CareerRiskItem[]> {
  return api.get(`/predictions/top-safe?limit=${limit}`);
}

export function fetchIndustryBreakdown(): Promise<IndustryBreakdown[]> {
  return api.get('/predictions/industry-breakdown');
}

export function fetchTimeline(): Promise<TimelineItem[]> {
  return api.get('/predictions/timeline');
}

export function fetchStats(): Promise<PlatformStats> {
  return api.get('/predictions/stats');
}

export function compareCareers(ids: number[]): Promise<{ careers: CareerDetail[] }> {
  return api.post('/compare', { career_ids: ids });
}

export function fetchCareerDNA(data: {
  skills: string[];
  interests: string[];
  education: string;
  salary_min?: number;
  salary_max?: number;
  max_risk?: number;
}): Promise<CareerDNAResponse> {
  return api.post('/recommendations/career-dna', data);
}
