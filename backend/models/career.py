from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.db.database import Base


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    onet_code = Column(String(10), unique=True, index=True)
    bls_code = Column(String(10), nullable=True)
    title = Column(String(200), nullable=False, index=True)
    category = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    median_salary = Column(Float, nullable=True)
    employment_count = Column(Integer, nullable=True)
    growth_rate_pct = Column(Float, nullable=True)
    education_level = Column(String(50), nullable=True)
    experience_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="career", cascade="all, delete-orphan")
    ensemble_prediction = relationship("EnsemblePrediction", back_populates="career",
                                       uselist=False, cascade="all, delete-orphan")
