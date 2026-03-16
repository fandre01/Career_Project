from pydantic import BaseModel
from typing import Optional


class CareerRiskItem(BaseModel):
    career_id: int
    title: str
    category: Optional[str] = None
    automation_risk_score: float
    disruption_year: Optional[int] = None
    risk_level: str
    median_salary: Optional[float] = None

    class Config:
        from_attributes = True


class IndustryBreakdown(BaseModel):
    category: str
    avg_risk_score: float
    career_count: int
    avg_salary: Optional[float] = None


class TimelineItem(BaseModel):
    career_id: int
    title: str
    category: Optional[str] = None
    disruption_year: Optional[int] = None
    automation_risk_score: float
    risk_level: str


class PlatformStats(BaseModel):
    total_careers: int
    avg_risk_score: float
    safest_category: str
    riskiest_category: str
    careers_at_high_risk: int
    careers_at_low_risk: int
