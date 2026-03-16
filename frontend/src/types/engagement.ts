export interface Comment {
  id: number;
  name: string;
  message: string;
  created_at: string;
}

export interface PaginatedComments {
  items: Comment[];
  total: number;
  page: number;
  page_size: number;
}

export interface ViewStats {
  total_views: number;
  today_views: number;
  unique_visitors: number;
}
