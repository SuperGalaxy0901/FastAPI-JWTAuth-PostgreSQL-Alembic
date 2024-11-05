from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: datetime


class Subscription(SubscriptionBase):
    id: int
    price: float
    is_active: bool

    class Config:
        form_attributes = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    user_id: Optional[int] = None
    magazine_id: Optional[int] = None
    plan_id: Optional[int] = None
    renewal_date: Optional[datetime] = None