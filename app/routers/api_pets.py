import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Pet, Shelter
from app.schemas import PetOut, PetCreate

router = APIRouter(prefix="/api/pets", tags=["Pets API"])

@router.get("", response_model=List[PetOut])
def get_pets(
    species: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,
    status: Optional[str] = None,
    shelter_id: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search and filter pets by species, size, gender, adoption status, shelter, or search query.
    """
    query = db.query(Pet)

    if species and species != "all":
        query = query.filter(Pet.species == species.lower())
    if size and size != "all":
        query = query.filter(Pet.size == size)
    if gender and gender != "all":
        query = query.filter(Pet.gender == gender)
    if status and status != "all":
        query = query.filter(Pet.status == status)
    if shelter_id:
        query = query.filter(Pet.shelter_id == shelter_id)
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Pet.name.ilike(search_pattern),
                Pet.breed.ilike(search_pattern),
                Pet.coat_color.ilike(search_pattern),
                Pet.personality.ilike(search_pattern)
            )
        )

    return query.order_by(Pet.created_at.desc()).all()


@router.get("/{pet_id}", response_model=PetOut)
def get_pet_by_id(pet_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed pet profile including shelter and full vaccine passport history."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.post("", response_model=PetOut, status_code=201)
def create_pet(pet_in: PetCreate, db: Session = Depends(get_db)):
    """Add a newly rescued animal to the shelter database."""
    shelter = db.query(Shelter).filter(Shelter.id == pet_in.shelter_id).first()
    if not shelter:
        raise HTTPException(status_code=400, detail="Specified shelter does not exist")

    pet = Pet(**pet_in.dict())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.patch("/{pet_id}/status")
def update_pet_status(pet_id: int, status: str = Query(..., pattern="^(available|pending|adopted)$"), db: Session = Depends(get_db)):
    """Update pet adoption status (available, pending, adopted)."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    pet.status = status
    db.commit()
    return {"message": "Status updated successfully", "pet_id": pet.id, "new_status": pet.status}


@router.post("/upload-photo")
async def upload_pet_photo(file: UploadFile = File(...)):
    """Upload a pet photo file and return the accessible static URL."""
    allowed_exts = [".jpg", ".jpeg", ".png", ".webp", ".svg"]
    filename = file.filename or "pet.jpg"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_exts:
        ext = ".jpg"

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "pets")
    os.makedirs(upload_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    target_path = os.path.join(upload_dir, unique_filename)

    content = await file.read()
    with open(target_path, "wb") as f:
        f.write(content)

    return {"photo_url": f"/static/uploads/pets/{unique_filename}"}

