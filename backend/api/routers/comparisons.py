from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from backend.db.database import get_db
from backend.models.career import Career
from backend.schemas.career import CareerCompareRequest, CareerCompareResponse, CareerDetail

router = APIRouter(prefix="/api/compare", tags=["comparisons"])


@router.post("", response_model=CareerCompareResponse)
def compare_careers(request: CareerCompareRequest, db: Session = Depends(get_db)):
    if len(request.career_ids) < 2 or len(request.career_ids) > 4:
        raise HTTPException(status_code=400, detail="Compare 2-4 careers at a time")

    careers = (
        db.query(Career)
        .options(
            joinedload(Career.skills),
            joinedload(Career.predictions),
            joinedload(Career.ensemble_prediction),
        )
        .filter(Career.id.in_(request.career_ids))
        .all()
    )

    if len(careers) != len(request.career_ids):
        raise HTTPException(status_code=404, detail="One or more careers not found")

    return CareerCompareResponse(careers=careers)
