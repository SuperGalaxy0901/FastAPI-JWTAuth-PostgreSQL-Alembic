from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, crud
from app.database import get_db

router = APIRouter(tags=["plans"])

@router.get("/plans/", response_model=List[schemas.Plan])
def get_plans(db: Session = Depends(get_db)):
    return crud.get_plans(db)

@router.post("/plans/", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return crud.create_plan(db=db, plan=plan)

@router.get("/plans/{plan_id}", response_model=schemas.Plan)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return crud.get_plan(db, plan_id)

@router.put("/plans/{plan_id}", response_model=schemas.Plan)
def update_plan(plan_id: int, plan: schemas.PlanUpdate, db: Session = Depends(get_db)):
    return crud.update_plan(db, plan_id, plan)

@router.delete("/plans/{plan_id}", response_model=schemas.Plan)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    return crud.delete_plan(db, plan_id)
