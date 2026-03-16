from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False, index=True)
    skill_name = Column(String(200), nullable=False)
    skill_category = Column(String(50), nullable=False)  # knowledge, skill, ability, task
    importance_score = Column(Float, default=0.0)
    automation_potential = Column(Float, default=0.0)  # 0.0 to 1.0

    career = relationship("Career", back_populates="skills")
