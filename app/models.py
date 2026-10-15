from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    city = Column(String(80), nullable=False, default="Bakı")
    address = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pets = relationship("Pet", back_populates="shelter", cascade="all, delete-orphan")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    species = Column(String(30), nullable=False, index=True)  # dog, cat, rabbit, bird, other
    breed = Column(String(80), nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female
    age_years = Column(Integer, default=1)
    age_months = Column(Integer, default=0)
    size = Column(String(20), default="Medium")  # Small, Medium, Large
    coat_color = Column(String(50), default="Mixed")
    description = Column(Text, nullable=True)
    personality = Column(String(150), nullable=True)  # comma-separated traits
    photo_url = Column(String(300), nullable=True)
    status = Column(String(30), default="available", index=True)  # available, pending, adopted
    energy_level = Column(Integer, default=3)  # 1 (low) to 5 (high)
    good_with_children = Column(Boolean, default=True)
    good_with_other_pets = Column(Boolean, default=True)
    house_trained = Column(Boolean, default=True)
    microchip_id = Column(String(50), unique=True, nullable=True)
    neutered = Column(Boolean, default=True)
    intake_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    shelter_id = Column(Integer, ForeignKey("shelters.id"), nullable=False)
    shelter = relationship("Shelter", back_populates="pets")

    vaccines = relationship("VaccineRecord", back_populates="pet", cascade="all, delete-orphan")
    applications = relationship("AdoptionApplication", back_populates="pet", cascade="all, delete-orphan")


class VaccineRecord(Base):
    __tablename__ = "vaccine_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    vaccine_name = Column(String(100), nullable=False)
    administered_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=True)
    batch_number = Column(String(50), nullable=True)
    vet_name = Column(String(100), default="Dr. Əliyev")
    clinic_name = Column(String(120), default="VetCare Bakı")
    status = Column(String(20), default="valid")  # valid, upcoming, overdue
    notes = Column(Text, nullable=True)

    pet = relationship("Pet", back_populates="vaccines")


class AdoptionApplication(Base):
    __tablename__ = "adoption_applications"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    applicant_name = Column(String(100), nullable=False)
    applicant_email = Column(String(100), nullable=False)
    applicant_phone = Column(String(50), nullable=False)
    applicant_city = Column(String(80), default="Bakı")
    living_space = Column(String(50), default="apartment")  # apartment, house_with_yard, countryside
    has_other_pets = Column(Boolean, default=False)
    has_children = Column(Boolean, default=False)
    experience_level = Column(String(50), default="intermediate")  # beginner, intermediate, experienced
    hours_alone_per_day = Column(Integer, default=4)
    message = Column(Text, nullable=True)
    status = Column(String(30), default="pending", index=True)  # pending, reviewing, approved, rejected
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pet = relationship("Pet", back_populates="applications")
