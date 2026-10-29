from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AdoptionApplication, Pet
from app.schemas import AdoptionApplicationCreate, AdoptionApplicationOut, AdoptionApplicationStatusUpdate
from app.auth import get_authenticated_user

router = APIRouter(prefix="/api/adoptions", tags=["Adoption Applications API"])

@router.post("", response_model=AdoptionApplicationOut, status_code=201)
def submit_adoption_application(app_in: AdoptionApplicationCreate, request: Request, db: Session = Depends(get_db)):
    """
    Submit an online adoption inquiry for a pet.
    Automatically flags pet status as 'pending' to alert shelter staff.
    If the applicant is signed in, the application is linked to their account
    so it appears on the "My Applications" page.
    """
    pet = db.query(Pet).filter(Pet.id == app_in.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Target pet not found")

    if pet.status == "adopted":
        raise HTTPException(status_code=400, detail="This pet has already been adopted")

    new_app = AdoptionApplication(**app_in.model_dump())
    user = get_authenticated_user(request)
    if user and user.get("user_id") and user["user_id"] > 0:
        new_app.user_id = user["user_id"]
    db.add(new_app)

    # Set pet status to pending if it was available
    if pet.status == "available":
        pet.status = "pending"

    db.commit()
    db.refresh(new_app)
    return new_app


@router.get("", response_model=List[AdoptionApplicationOut])
def list_adoption_applications(
    status: Optional[str] = None,
    pet_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List adoption applications for shelter staff.
    Supports filtering by status (pending, reviewing, approved, rejected).
    """
    query = db.query(AdoptionApplication)
    if status and status != "all":
        query = query.filter(AdoptionApplication.status == status)
    if pet_id:
        query = query.filter(AdoptionApplication.pet_id == pet_id)

    return query.order_by(AdoptionApplication.created_at.desc()).all()


@router.patch("/{app_id}/status", response_model=AdoptionApplicationOut)
def update_application_status(
    app_id: int,
    status_update: AdoptionApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Shelter admin workflow: approve, reject, or mark under review.
    If approved, marks pet status as 'adopted'.
    If rejected and no other pending applications exist, marks pet status back to 'available'.
    """
    app = db.query(AdoptionApplication).filter(AdoptionApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = status_update.status
    if status_update.review_notes is not None:
        app.review_notes = status_update.review_notes

    # Synchronize pet status
    pet = db.query(Pet).filter(Pet.id == app.pet_id).first()
    if pet:
        if app.status == "approved":
            pet.status = "adopted"
        elif app.status == "rejected":
            # Check if there are other pending applications for this pet
            pending_count = db.query(AdoptionApplication).filter(
                AdoptionApplication.pet_id == pet.id,
                AdoptionApplication.id != app.id,
                AdoptionApplication.status.in_(["pending", "reviewing"])
            ).count()
            if pending_count == 0:
                pet.status = "available"

    db.commit()
    db.refresh(app)
    return app
