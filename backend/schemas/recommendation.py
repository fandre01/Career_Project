from pydantic import BaseModel
from typing import Optional


class CareerDNARequest(BaseModel):
    skills: list[str]
    interests: list[str]
    education: str  # "high_school", "bachelors", "masters", "doctorate"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    max_risk: Optional[float] = 60.0


class CareerMatch(BaseModel):
    career_id: int
    title: str
    category: Optional[str] = None
    match_score: float  # 0-100
    automation_risk_score: float
    risk_level: str
    median_salary: Optional[float] = None
    disruption_year: Optional[int] = None
    matching_skills: list[str]


class CareerDNAResponse(BaseModel):
    matches: list[CareerMatch]
    total_analyzed: int
