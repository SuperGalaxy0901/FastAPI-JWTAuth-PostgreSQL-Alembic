from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.plan import Plan

class MagazineBase(BaseModel):
    name: str
    description: str
    base_price: float


class Magazine(MagazineBase):
    id: int
    plans: List[Plan] = []

    class Config:
        form_attributes = True


class MagazineCreate(MagazineBase):
    pass


class MagazineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None