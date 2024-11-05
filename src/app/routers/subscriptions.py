from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, crud
from app.dependencies import get_db, get_current_user

router = APIRouter(tags=["subscriptions"])


@router.get("/subscriptions/", response_model=List[schemas.Subscription])
def get_subscriptions(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_subscriptions(db)


@router.post("/subscriptions/", response_model=schemas.Subscription)
def create_subscription(
    subscription: schemas.SubscriptionCreate,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.create_subscription(db=db, subscription=subscription)


@router.get("/subscriptions/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    return crud.get_subscription(db, subscription_id)


@router.put("/subscriptions/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int,
    subscription: schemas.SubscriptionUpdate,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.update_subscription(db, subscription_id, subscription)


@router.delete("/subscriptions/{subscription_id}", response_model=schemas.Subscription)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.deactivate_subscription(db, subscription_id, user_id=current_user.id)
