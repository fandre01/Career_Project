from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.db.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False, index=True)
    model_name = Column(String(50), nullable=False)
    automation_risk_score = Column(Float, nullable=False)
    disruption_year = Column(Integer, nullable=True)
    salary_impact_pct = Column(Float, nullable=True)
    job_stability_score = Column(Float, nullable=True)
    confidence_interval_low = Column(Float, nullable=True)
    confidence_interval_high = Column(Float, nullable=True)
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    career = relationship("Career", back_populates="predictions")


class EnsemblePrediction(Base):
    __tablename__ = "ensemble_predictions"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False, unique=True, index=True)
    automation_risk_score = Column(Float, nullable=False)
    disruption_year = Column(Integer, nullable=True)
    salary_5yr_projection = Column(Float, nullable=True)
    salary_10yr_projection = Column(Float, nullable=True)
    job_stability_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    predicted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    career = relationship("Career", back_populates="ensemble_prediction")
