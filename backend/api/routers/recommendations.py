from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from backend.db.database import get_db
from backend.models.career import Career
from backend.models.prediction import EnsemblePrediction
from backend.models.skill import CareerSkill
from backend.schemas.recommendation import CareerDNARequest, CareerDNAResponse, CareerMatch
from typing import Optional

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post("/career-dna", response_model=CareerDNAResponse)
def career_dna(request: CareerDNARequest, db: Session = Depends(get_db)):
    query = (
        db.query(Career)
        .options(joinedload(Career.skills), joinedload(Career.ensemble_prediction))
        .join(EnsemblePrediction)
        .filter(EnsemblePrediction.automation_risk_score <= request.max_risk)
    )

    if request.salary_min is not None:
        query = query.filter(Career.median_salary >= request.salary_min)
    if request.salary_max is not None:
        query = query.filter(Career.median_salary <= request.salary_max)

    education_order = {"high_school": 1, "bachelors": 2, "masters": 3, "doctorate": 4}
    edu_map = {
        "high_school": ["No formal educational credential", "High school diploma or equivalent",
                        "Some college, no degree", "Postsecondary nondegree award"],
        "bachelors": ["No formal educational credential", "High school diploma or equivalent",
                      "Some college, no degree", "Postsecondary nondegree award",
                      "Associate's degree", "Bachelor's degree"],
        "masters": ["No formal educational credential", "High school diploma or equivalent",
                    "Some college, no degree", "Postsecondary nondegree award",
                    "Associate's degree", "Bachelor's degree", "Master's degree"],
        "doctorate": ["No formal educational credential", "High school diploma or equivalent",
                      "Some college, no degree", "Postsecondary nondegree award",
                      "Associate's degree", "Bachelor's degree", "Master's degree",
                      "Doctoral or professional degree"],
    }

    allowed_edu = edu_map.get(request.education, edu_map["bachelors"])
    query = query.filter(Career.education_level.in_(allowed_edu))

    careers = query.all()
    user_keywords = set(k.lower() for k in request.skills + request.interests)

    matches = []
    for career in careers:
        career_keywords = set()
        for skill in career.skills:
            career_keywords.add(skill.skill_name.lower())
            for word in skill.skill_name.lower().split():
                career_keywords.add(word)

        title_words = set(career.title.lower().split())
        category_words = set((career.category or "").lower().split())
        career_keywords.update(title_words)
        career_keywords.update(category_words)

        overlap = user_keywords & career_keywords
        if not overlap and not user_keywords:
            match_score = 50.0
        elif not overlap:
            match_score = 10.0
        else:
            match_score = min(100, (len(overlap) / max(len(user_keywords), 1)) * 100)

        ep = career.ensemble_prediction
        if ep:
            resilience_bonus = (100 - ep.automation_risk_score) * 0.2
            match_score = min(100, match_score * 0.7 + resilience_bonus + 10)

        matches.append(CareerMatch(
            career_id=career.id,
            title=career.title,
            category=career.category,
            match_score=round(match_score, 1),
            automation_risk_score=ep.automation_risk_score if ep else 50.0,
            risk_level=ep.risk_level if ep else "medium",
            median_salary=career.median_salary,
            disruption_year=ep.disruption_year if ep else None,
            matching_skills=list(overlap)[:10],
        ))

    matches.sort(key=lambda m: m.match_score, reverse=True)
    return CareerDNAResponse(matches=matches[:20], total_analyzed=len(careers))


@router.get("/majors")
def recommended_majors(
    risk_max: float = Query(40, ge=0, le=100),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Career, EnsemblePrediction)
        .join(EnsemblePrediction)
        .filter(EnsemblePrediction.automation_risk_score <= risk_max)
        .order_by(Career.median_salary.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "career_id": c.id,
            "title": c.title,
            "category": c.category,
            "median_salary": c.median_salary,
            "automation_risk_score": ep.automation_risk_score,
            "risk_level": ep.risk_level,
            "education_level": c.education_level,
        }
        for c, ep in results
    ]
