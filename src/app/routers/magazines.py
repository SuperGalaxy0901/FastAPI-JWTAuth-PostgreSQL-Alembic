from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas, models, crud
from app.database import get_db

router = APIRouter(tags=["magazines"])


@router.get("/magazines/", response_model=List[schemas.Magazine])
def get_magazines(db: Session = Depends(get_db)):
    return crud.get_magazines(db)


@router.post("/magazines/", response_model=schemas.Magazine)
def create_magazine(magazine: schemas.MagazineCreate, db: Session = Depends(get_db)):
    return crud.create_magazine(db=db, magazine=magazine)


@router.get("/magazines/{magazine_id}", response_model=schemas.Magazine)
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    return crud.get_magazine(db, magazine_id)


@router.put("/magazines/{magazine_id}", response_model=schemas.Magazine)
def update_magazine(
    magazine_id: int, magazine: schemas.MagazineUpdate, db: Session = Depends(get_db)
):
    return crud.update_magazine(db, magazine_id, magazine)


@router.delete("/magazines/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    return crud.delete_magazine(db, magazine_id)
