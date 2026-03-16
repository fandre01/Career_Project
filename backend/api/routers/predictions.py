from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.database import get_db
from backend.models.career import Career
from backend.models.prediction import Prediction, EnsemblePrediction
from backend.schemas.prediction import (
    CareerRiskItem,
    IndustryBreakdown,
    TimelineItem,
    PlatformStats,
)
from backend.schemas.career import PredictionSchema

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/top-risk", response_model=list[CareerRiskItem])
def top_risk_careers(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Career, EnsemblePrediction)
        .join(EnsemblePrediction)
        .order_by(EnsemblePrediction.automation_risk_score.desc())
        .limit(limit)
        .all()
    )
    return [
        CareerRiskItem(
            career_id=c.id,
            title=c.title,
            category=c.category,
            automation_risk_score=ep.automation_risk_score,
            disruption_year=ep.disruption_year,
            risk_level=ep.risk_level,
            median_salary=c.median_salary,
        )
        for c, ep in results
    ]


@router.get("/top-safe", response_model=list[CareerRiskItem])
def top_safe_careers(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Career, EnsemblePrediction)
        .join(EnsemblePrediction)
        .order_by(EnsemblePrediction.automation_risk_score.asc())
        .limit(limit)
        .all()
    )
    return [
        CareerRiskItem(
            career_id=c.id,
            title=c.title,
            category=c.category,
            automation_risk_score=ep.automation_risk_score,
            disruption_year=ep.disruption_year,
            risk_level=ep.risk_level,
            median_salary=c.median_salary,
        )
        for c, ep in results
    ]


@router.get("/industry-breakdown", response_model=list[IndustryBreakdown])
def industry_breakdown(db: Session = Depends(get_db)):
    results = (
        db.query(
            Career.category,
            func.avg(EnsemblePrediction.automation_risk_score),
            func.count(Career.id),
            func.avg(Career.median_salary),
        )
        .join(EnsemblePrediction)
        .group_by(Career.category)
        .order_by(func.avg(EnsemblePrediction.automation_risk_score).desc())
        .all()
    )
    return [
        IndustryBreakdown(
            category=r[0] or "Other",
            avg_risk_score=round(r[1], 1),
            career_count=r[2],
            avg_salary=round(r[3], 0) if r[3] else None,
        )
        for r in results
    ]


@router.get("/timeline", response_model=list[TimelineItem])
def timeline(db: Session = Depends(get_db)):
    results = (
        db.query(Career, EnsemblePrediction)
        .join(EnsemblePrediction)
        .filter(EnsemblePrediction.disruption_year.isnot(None))
        .order_by(EnsemblePrediction.disruption_year.asc())
        .all()
    )
    return [
        TimelineItem(
            career_id=c.id,
            title=c.title,
            category=c.category,
            disruption_year=ep.disruption_year,
            automation_risk_score=ep.automation_risk_score,
            risk_level=ep.risk_level,
        )
        for c, ep in results
    ]


@router.get("/stats", response_model=PlatformStats)
def platform_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Career.id)).scalar()
    avg_risk = db.query(func.avg(EnsemblePrediction.automation_risk_score)).scalar() or 0

    safest = (
        db.query(Career.category, func.avg(EnsemblePrediction.automation_risk_score).label("avg_risk"))
        .join(EnsemblePrediction)
        .group_by(Career.category)
        .order_by(func.avg(EnsemblePrediction.automation_risk_score).asc())
        .first()
    )
    riskiest = (
        db.query(Career.category, func.avg(EnsemblePrediction.automation_risk_score).label("avg_risk"))
        .join(EnsemblePrediction)
        .group_by(Career.category)
        .order_by(func.avg(EnsemblePrediction.automation_risk_score).desc())
        .first()
    )

    high_risk = db.query(func.count(EnsemblePrediction.id)).filter(
        EnsemblePrediction.risk_level.in_(["high", "critical"])
    ).scalar()
    low_risk = db.query(func.count(EnsemblePrediction.id)).filter(
        EnsemblePrediction.risk_level == "low"
    ).scalar()

    return PlatformStats(
        total_careers=total or 0,
        avg_risk_score=round(avg_risk, 1),
        safest_category=safest[0] if safest else "N/A",
        riskiest_category=riskiest[0] if riskiest else "N/A",
        careers_at_high_risk=high_risk or 0,
        careers_at_low_risk=low_risk or 0,
    )


@router.get("/{career_id}", response_model=list[PredictionSchema])
def career_predictions(career_id: int, db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.career_id == career_id)
        .all()
    )
    return predictions
