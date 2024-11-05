from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class PlanBase(BaseModel):
    title: str
    description: str
    renewal_period: int
    tier: int
    discount: float
    magazine_id: Optional[int] = None


class PlanCreate(PlanBase):
    pass


class Plan(PlanBase):
    id: int

    class Config:
        form_attributes = True


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    renewal_period: Optional[int] = None
    tier: Optional[int] = None
    discount: Optional[float] = None
    magazine_id: Optional[int] = None