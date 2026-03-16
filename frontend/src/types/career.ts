export interface EnsemblePrediction {
  automation_risk_score: number;
  disruption_year: number | null;
  salary_5yr_projection: number | null;
  salary_10yr_projection: number | null;
  job_stability_score: number | null;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface CareerSkill {
  id: number;
  skill_name: string;
  skill_category: string;
  importance_score: number;
  automation_potential: number;
}

export interface Prediction {
  id: number;
  model_name: string;
  automation_risk_score: number;
  disruption_year: number | null;
  salary_impact_pct: number | null;
  job_stability_score: number | null;
  confidence_interval_low: number | null;
  confidence_interval_high: number | null;
}

export interface CareerListItem {
  id: number;
  onet_code: string;
  title: string;
  category: string | null;
  median_salary: number | null;
  education_level: string | null;
  growth_rate_pct: number | null;
  ensemble_prediction: EnsemblePrediction | null;
}

export interface CareerDetail extends CareerListItem {
  bls_code: string | null;
  description: string | null;
  employment_count: number | null;
  experience_level: string | null;
  skills: CareerSkill[];
  predictions: Prediction[];
}

export interface PaginatedCareers {
  items: CareerListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CareerRiskItem {
  career_id: number;
  title: string;
  category: string | null;
  automation_risk_score: number;
  disruption_year: number | null;
  risk_level: string;
  median_salary: number | null;
}

export interface IndustryBreakdown {
  category: string;
  avg_risk_score: number;
  career_count: number;
  avg_salary: number | null;
}

export interface TimelineItem {
  career_id: number;
  title: string;
  category: string | null;
  disruption_year: number | null;
  automation_risk_score: number;
  risk_level: string;
}

export interface PlatformStats {
  total_careers: number;
  avg_risk_score: number;
  safest_category: string;
  riskiest_category: string;
  careers_at_high_risk: number;
  careers_at_low_risk: number;
}

export interface CareerMatch {
  career_id: number;
  title: string;
  category: string | null;
  match_score: number;
  automation_risk_score: number;
  risk_level: string;
  median_salary: number | null;
  disruption_year: number | null;
  matching_skills: string[];
}

export interface CareerDNAResponse {
  matches: CareerMatch[];
  total_analyzed: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
