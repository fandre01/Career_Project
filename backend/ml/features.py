"""
Feature engineering for career automation risk prediction.
Extracts features from the database for ML model training.
"""
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.models.career import Career
from backend.models.skill import CareerSkill
from backend.models.prediction import EnsemblePrediction


EDUCATION_YEARS = {
    "No formal educational credential": 10,
    "High school diploma or equivalent": 12,
    "Some college, no degree": 13,
    "Postsecondary nondegree award": 13,
    "Associate's degree": 14,
    "Bachelor's degree": 16,
    "Master's degree": 18,
    "Doctoral or professional degree": 22,
}


def extract_features(db: Session) -> pd.DataFrame:
    careers = db.query(Career).all()
    records = []

    for career in careers:
        skills = db.query(CareerSkill).filter(CareerSkill.career_id == career.id).all()

        # Aggregate skill-level features
        if skills:
            importance_scores = [s.importance_score for s in skills]
            automation_potentials = [s.automation_potential for s in skills]
            knowledge_skills = [s for s in skills if s.skill_category == "knowledge"]
            ability_skills = [s for s in skills if s.skill_category == "ability"]
            task_skills = [s for s in skills if s.skill_category == "skill"]

            avg_automation = np.mean(automation_potentials)
            weighted_automation = (
                np.average(automation_potentials, weights=importance_scores)
                if sum(importance_scores) > 0 else avg_automation
            )
            max_automation = max(automation_potentials)
            min_automation = min(automation_potentials)
            std_automation = np.std(automation_potentials)
            avg_importance = np.mean(importance_scores)
            num_skills = len(skills)
            num_knowledge = len(knowledge_skills)
            num_abilities = len(ability_skills)
            num_task_skills = len(task_skills)

            # Human-edge features
            human_skills = [s for s in skills if s.automation_potential < 0.3]
            pct_human_edge = len(human_skills) / len(skills) if skills else 0

            # Tech exposure
            tech_skills = [s for s in skills if any(
                kw in s.skill_name.lower()
                for kw in ["programming", "computer", "software", "data", "technology", "systems"]
            )]
            tech_exposure = len(tech_skills) / len(skills) if skills else 0
        else:
            avg_automation = weighted_automation = 0.5
            max_automation = min_automation = std_automation = 0
            avg_importance = num_skills = num_knowledge = num_abilities = num_task_skills = 0
            pct_human_edge = tech_exposure = 0

        education_years = EDUCATION_YEARS.get(career.education_level, 14)

        record = {
            "career_id": career.id,
            "title": career.title,
            "category": career.category,
            "median_salary": career.median_salary or 50000,
            "employment_count": career.employment_count or 100000,
            "growth_rate_pct": career.growth_rate_pct or 0,
            "education_years": education_years,
            "avg_automation_potential": round(avg_automation, 4),
            "weighted_automation_potential": round(weighted_automation, 4),
            "max_automation_potential": round(max_automation, 4),
            "min_automation_potential": round(min_automation, 4),
            "std_automation_potential": round(std_automation, 4),
            "avg_skill_importance": round(avg_importance, 2),
            "num_skills": num_skills,
            "num_knowledge_areas": num_knowledge,
            "num_abilities": num_abilities,
            "num_task_skills": num_task_skills,
            "pct_human_edge_skills": round(pct_human_edge, 4),
            "tech_exposure_score": round(tech_exposure, 4),
            "salary_log": round(np.log1p(career.median_salary or 50000), 4),
            "employment_log": round(np.log1p(career.employment_count or 100000), 4),
        }

        # Target: get ensemble prediction if exists
        ep = db.query(EnsemblePrediction).filter(
            EnsemblePrediction.career_id == career.id
        ).first()
        if ep:
            record["automation_risk_score"] = ep.automation_risk_score
            record["disruption_year"] = ep.disruption_year
            record["job_stability_score"] = ep.job_stability_score

        records.append(record)

    df = pd.DataFrame(records)
    return df


FEATURE_COLUMNS = [
    "median_salary", "employment_count", "growth_rate_pct", "education_years",
    "avg_automation_potential", "weighted_automation_potential",
    "max_automation_potential", "min_automation_potential", "std_automation_potential",
    "avg_skill_importance", "num_skills", "num_knowledge_areas",
    "num_abilities", "num_task_skills", "pct_human_edge_skills",
    "tech_exposure_score", "salary_log", "employment_log",
]

TARGET_COLUMNS = ["automation_risk_score", "disruption_year", "job_stability_score"]
