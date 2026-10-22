from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# --- Shelter Schemas ---
class ShelterBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Bakı Heyvanları Xilasetmə Mərkəzi"})
    city: str = Field(..., json_schema_extra={"example": "Bakı"})
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

class ShelterCreate(ShelterBase):
    pass

class ShelterOut(ShelterBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Vaccine Schemas ---
class VaccineBase(BaseModel):
    vaccine_name: str
    administered_date: date
    next_due_date: Optional[date] = None
    batch_number: Optional[str] = None
    vet_name: Optional[str] = "Dr. Əliyev"
    clinic_name: Optional[str] = "VetCare Bakı"
    status: Optional[str] = "valid"
    notes: Optional[str] = None

class VaccineCreate(VaccineBase):
    pet_id: int

class VaccineOut(VaccineBase):
    id: int
    pet_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Pet Schemas ---
class PetBase(BaseModel):
    name: str
    species: str
    breed: str
    gender: str
    age_years: int = 1
    age_months: int = 0
    size: str = "Medium"
    coat_color: str = "Mixed"
    description: Optional[str] = None
    personality: Optional[str] = None
    photo_url: Optional[str] = None
    status: str = "available"
    energy_level: int = 3
    good_with_children: bool = True
    good_with_other_pets: bool = True
    house_trained: bool = True
    microchip_id: Optional[str] = None
    neutered: bool = True
    intake_date: Optional[date] = None
    shelter_id: int

class PetCreate(PetBase):
    pass

class PetOut(PetBase):
    id: int
    created_at: datetime
    shelter: Optional[ShelterOut] = None
    vaccines: List[VaccineOut] = []
    model_config = ConfigDict(from_attributes=True)


# --- Adoption Application Schemas ---
class AdoptionApplicationCreate(BaseModel):
    pet_id: int
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    applicant_city: str = "Bakı"
    living_space: str = "apartment"
    has_other_pets: bool = False
    has_children: bool = False
    experience_level: str = "intermediate"
    hours_alone_per_day: int = 4
    message: Optional[str] = None

class AdoptionApplicationStatusUpdate(BaseModel):
    status: str  # pending, reviewing, approved, rejected
    review_notes: Optional[str] = None

class AdoptionApplicationOut(BaseModel):
    id: int
    pet_id: int
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    applicant_city: str
    living_space: str
    has_other_pets: bool
    has_children: bool
    experience_level: str
    hours_alone_per_day: int
    message: Optional[str]
    status: str
    review_notes: Optional[str]
    created_at: datetime
    pet: Optional[PetBase] = None
    model_config = ConfigDict(from_attributes=True)


# --- Smart Matcher Quiz Schema ---
class QuizAnswers(BaseModel):
    living_space: str = "apartment"  # apartment, house_with_yard, countryside
    daily_time: Optional[int] = 2    # 1 (<30m), 2 (30-60m), 3 (1-2h), 4 (2h+)
    experience_level: Optional[str] = "intermediate"  # beginner, intermediate, experienced
    energy_preference: int = 3       # 1 to 5
    has_children: bool = False
    has_other_pets: bool = False
    shedding_preference: Optional[str] = "any"  # low_shedding, any
    preferred_species: Optional[str] = "any"
    preferred_size: Optional[str] = "any"
