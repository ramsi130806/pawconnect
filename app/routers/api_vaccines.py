from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import VaccineRecord, Pet
from app.schemas import VaccineCreate, VaccineOut

router = APIRouter(prefix="/api/vaccines", tags=["Vaccine Passport API"])

@router.post("", response_model=VaccineOut, status_code=201)
def add_vaccine_record(vaccine_in: VaccineCreate, db: Session = Depends(get_db)):
    """Add a new medical/vaccine log entry to a pet's digital passport."""
    pet = db.query(Pet).filter(Pet.id == vaccine_in.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Target pet not found")

    status = "valid"
    if vaccine_in.next_due_date and vaccine_in.next_due_date < date.today():
        status = "overdue"

    record = VaccineRecord(
        pet_id=vaccine_in.pet_id,
        vaccine_name=vaccine_in.vaccine_name,
        administered_date=vaccine_in.administered_date,
        next_due_date=vaccine_in.next_due_date,
        batch_number=vaccine_in.batch_number,
        vet_name=vaccine_in.vet_name,
        clinic_name=vaccine_in.clinic_name,
        status=status,
        notes=vaccine_in.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/pet/{pet_id}", response_model=List[VaccineOut])
def get_pet_vaccines(pet_id: int, db: Session = Depends(get_db)):
    """Retrieve full vaccine history for a specific pet."""
    return db.query(VaccineRecord).filter(VaccineRecord.pet_id == pet_id).order_by(VaccineRecord.administered_date.desc()).all()


@router.get("/alerts/overdue", response_model=List[VaccineOut])
def get_overdue_vaccine_alerts(db: Session = Depends(get_db)):
    """Retrieve all vaccines that have reached their expiration or due date."""
    today = date.today()
    return db.query(VaccineRecord).filter(
        VaccineRecord.next_due_date != None,
        VaccineRecord.next_due_date < today
    ).all()
