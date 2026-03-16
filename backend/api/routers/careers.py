from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from backend.db.database import get_db
from backend.models.career import Career
from backend.models.prediction import EnsemblePrediction
from backend.schemas.career import CareerDetail, CareerListItem, PaginatedCareers
from typing import Optional
import math

router = APIRouter(prefix="/api/careers", tags=["careers"])


@router.get("", response_model=PaginatedCareers)
def list_careers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query("title", pattern="^(title|median_salary|risk_score|growth_rate)$"),
    sort_order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    query = db.query(Career).options(joinedload(Career.ensemble_prediction))

    if category:
        query = query.filter(Career.category == category)
    if salary_min is not None:
        query = query.filter(Career.median_salary >= salary_min)
    if salary_max is not None:
        query = query.filter(Career.median_salary <= salary_max)
    if search:
        query = query.filter(Career.title.ilike(f"%{search}%"))
    if risk_level:
        query = query.join(EnsemblePrediction).filter(EnsemblePrediction.risk_level == risk_level)

    total = query.count()

    if sort_by == "risk_score":
        query = query.join(EnsemblePrediction, isouter=True)
        order_col = EnsemblePrediction.automation_risk_score
    elif sort_by == "median_salary":
        order_col = Career.median_salary
    elif sort_by == "growth_rate":
        order_col = Career.growth_rate_pct
    else:
        order_col = Career.title

    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedCareers(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Career.category, func.count(Career.id))
        .group_by(Career.category)
        .order_by(Career.category)
        .all()
    )
    return [{"name": c[0], "count": c[1]} for c in categories if c[0]]


@router.get("/search")
def search_careers(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    careers = (
        db.query(Career)
        .options(joinedload(Career.ensemble_prediction))
        .filter(Career.title.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    return [CareerListItem.model_validate(c) for c in careers]


@router.get("/{career_id}", response_model=CareerDetail)
def get_career(career_id: int, db: Session = Depends(get_db)):
    career = (
        db.query(Career)
        .options(
            joinedload(Career.skills),
            joinedload(Career.predictions),
            joinedload(Career.ensemble_prediction),
        )
        .filter(Career.id == career_id)
        .first()
    )
    if not career:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Career not found")
    return career
