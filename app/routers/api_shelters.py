from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Shelter
from app.schemas import ShelterOut, ShelterCreate

router = APIRouter(prefix="/api/shelters", tags=["Shelters API"])

@router.get("", response_model=List[ShelterOut])
def list_shelters(db: Session = Depends(get_db)):
    """Retrieve all accredited animal rescue shelters."""
    return db.query(Shelter).all()

@router.get("/{shelter_id}", response_model=ShelterOut)
def get_shelter(shelter_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific shelter."""
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return shelter

@router.post("", response_model=ShelterOut, status_code=201)
def create_shelter(shelter_in: ShelterCreate, db: Session = Depends(get_db)):
    """Register a new partner animal shelter."""
    shelter = Shelter(**shelter_in.dict())
    db.add(shelter)
    db.commit()
    db.refresh(shelter)
    return shelter
