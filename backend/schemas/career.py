from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CareerSkillSchema(BaseModel):
    id: int
    skill_name: str
    skill_category: str
    importance_score: float
    automation_potential: float

    class Config:
        from_attributes = True


class EnsemblePredictionSchema(BaseModel):
    automation_risk_score: float
    disruption_year: Optional[int] = None
    salary_5yr_projection: Optional[float] = None
    salary_10yr_projection: Optional[float] = None
    job_stability_score: Optional[float] = None
    risk_level: str

    class Config:
        from_attributes = True


class PredictionSchema(BaseModel):
    id: int
    model_name: str
    automation_risk_score: float
    disruption_year: Optional[int] = None
    salary_impact_pct: Optional[float] = None
    job_stability_score: Optional[float] = None
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None

    class Config:
        from_attributes = True


class CareerListItem(BaseModel):
    id: int
    onet_code: str
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    median_salary: Optional[float] = None
    education_level: Optional[str] = None
    growth_rate_pct: Optional[float] = None
    ensemble_prediction: Optional[EnsemblePredictionSchema] = None

    class Config:
        from_attributes = True


class CareerDetail(BaseModel):
    id: int
    onet_code: str
    bls_code: Optional[str] = None
    title: str
    category: Optional[str] = None
    description: Optional[str] = None
    median_salary: Optional[float] = None
    employment_count: Optional[int] = None
    growth_rate_pct: Optional[float] = None
    education_level: Optional[str] = None
    experience_level: Optional[str] = None
    skills: list[CareerSkillSchema] = []
    predictions: list[PredictionSchema] = []
    ensemble_prediction: Optional[EnsemblePredictionSchema] = None

    class Config:
        from_attributes = True


class CareerCompareRequest(BaseModel):
    career_ids: list[int]


class CareerCompareResponse(BaseModel):
    careers: list[CareerDetail]


class PaginatedCareers(BaseModel):
    items: list[CareerListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
