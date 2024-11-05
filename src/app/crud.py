from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def reset_user_password(db: Session, email: str, new_password: str):
    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    user.is_active = False
    db.commit()
    return user


def get_magazines(db: Session):
    return db.query(models.Magazine).all()


def create_magazine(db: Session, magazine: schemas.MagazineCreate):
    db_magazine = models.Magazine(
        name=magazine.name,
        description=magazine.description,
        base_price=magazine.base_price,
    )
    db.add(db_magazine)
    db.commit()
    db.refresh(db_magazine)
    return db_magazine


def get_magazine(db: Session, magazine_id: int):
    magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )
    if magazine is None:
        raise HTTPException(status_code=404, detail="Magazine not found")


def update_magazine(
    db: Session, magazine_id: int, magazine_update: schemas.MagazineUpdate
):
    db_magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )

    if db_magazine is None:
        return None

    db_magazine.description = magazine_update.description
    db_magazine.name = magazine_update.name
    db_magazine.base_price = magazine_update.base_price

    db.commit()
    db.refresh(db_magazine)
    return db_magazine


def delete_magazine(db: Session, magazine_id: int):
    db_magazine = (
        db.query(models.Magazine).filter(models.Magazine.id == magazine_id).first()
    )

    if db_magazine is None:
        raise None

    db.delete(db_magazine)
    db.commit()
    return db_magazine


def calculate_subscription_price(base_price: float, discount: float) -> float:
    return base_price * (1 - discount)


def create_subscription(db: Session, subscription: schemas.SubscriptionCreate):
    db_subscription = (
        db.query(models.Subscription)
        .filter(
            models.Subscription.user_id == subscription.user_id,
            models.Subscription.magazine_id == subscription.magazine_id,
            models.Subscription.plan_id == subscription.plan_id,
        )
        .first()
    )

    if db_subscription:
        raise HTTPException(status_code=422, detail="Subscription already exists")

    magazine = (
        db.query(models.Magazine)
        .filter(models.Magazine.id == subscription.magazine_id)
        .first()
    )
    plan = db.query(models.Plan).filter(models.Plan.id == subscription.plan_id).first()

    if not magazine or not plan:
        raise HTTPException(status_code=404, detail="Magazine or Plan not found")

    price = calculate_subscription_price(magazine.base_price, plan.discount)

    if price <= 0:
        raise HTTPException(status_code=422, detail="Price must be greater than zero")

    db_subscription = models.Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
        price=price,
        renewal_date=subscription.renewal_date,
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def update_subscription(
    db: Session, subscription_id: int, subscription_update: schemas.SubscriptionUpdate
):
    db_subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == subscription_id)
        .first()
    )

    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    magazine = (
        db.query(models.Magazine)
        .filter(models.Magazine.id == db_subscription.magazine_id)
        .first()
    )
    plan = (
        db.query(models.Plan).filter(models.Plan.id == db_subscription.plan_id).first()
    )

    if not magazine or not plan:
        raise HTTPException(status_code=404, detail="Magazine or Plan not found")

    price = calculate_subscription_price(magazine.base_price, plan.discount)

    db_subscription.user_id = subscription_update.user_id
    db_subscription.magazine_id = subscription_update.magazine_id
    db_subscription.plan_id = subscription_update.plan_id
    db_subscription.price = price
    db_subscription.renewal_date = subscription_update.renewal_date

    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def get_subscriptions(db: Session):
    subscriptions = db.query(models.Subscription).all()
    for subscription in subscriptions:
        db.delete(subscription)
    return subscriptions


def get_subscription(db: Session, subscription_id: int):
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == subscription_id)
        .first()
    )
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


def get_subscriptions_by_user(db: Session, user_id: int):
    return (
        db.query(models.Subscription)
        .filter(
            models.Subscription.user_id == user_id,
            models.Subscription.is_active == True,
        )
        .all()
    )


def deactivate_subscription(db: Session, subscription_id: int, user_id: int):
    subscription = (
        db.query(models.Subscription)
        .filter(
            models.Subscription.id == subscription_id,
            models.Subscription.user_id == user_id,
        )
        .first()
    )
    subscription.is_active = False
    db.commit()
    return subscription


def get_plans(db: Session):
    return db.query(models.Plan).all()


def create_plan(db: Session, plan: schemas.PlanCreate):
    if plan.renewal_period <= 0:
        raise HTTPException(
            status_code=422, detail="Renewal period must be greater than zero"
        )
    db_plan = models.Plan(
        title=plan.title,
        description=plan.description,
        renewal_period=plan.renewal_period,
        tier=plan.tier,
        discount=plan.discount,
        magazine_id=plan.magazine_id,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_plan(db: Session, plan_id: int):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


def update_plan(db: Session, plan_id: int, plan_update: schemas.PlanUpdate):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    db_plan.title = plan_update.title
    db_plan.description = plan_update.description
    db_plan.renewal_period = plan_update.renewal_period
    db_plan.tier = plan_update.tier
    db_plan.discount = plan_update.discount
    db_plan.magazine_id = plan_update.magazine_id

    db.commit()
    db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if db_plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(db_plan)
    db.commit()
    return db_plan
