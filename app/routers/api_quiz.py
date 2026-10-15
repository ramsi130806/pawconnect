from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pet
from app.schemas import QuizAnswers

router = APIRouter(prefix="/api/quiz", tags=["Smart Matcher Algorithm"])

@router.post("/match")
def calculate_matches(answers: QuizAnswers, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Intelligent Pet Compatibility Algorithm (Input -> Processing -> Output).
    Ranks available shelter pets based on applicant's home space, family structure,
    and lifestyle rhythm to reduce post-adoption returns.
    """
    pets = db.query(Pet).filter(Pet.status.in_(["available", "pending"])).all()
    results = []

    for pet in pets:
        score = 80  # Base compatibility baseline
        match_reasons = []

        # 1. Species preference filter / bonus
        if answers.preferred_species and answers.preferred_species != "any":
            if pet.species == answers.preferred_species.lower():
                score += 15
                match_reasons.append("Tələb olunan heyvan növünə tam uyğundur")
            else:
                score -= 30

        # 2. Size preference
        if answers.preferred_size and answers.preferred_size != "any":
            if pet.size == answers.preferred_size:
                score += 10
                match_reasons.append(f"{pet.size} ölçü seçiminizi qarşılayır")
            else:
                score -= 10

        # 3. Energy level proximity (1 to 5)
        energy_diff = abs(pet.energy_level - answers.energy_preference)
        energy_penalty = energy_diff * 8
        score -= energy_penalty
        if energy_diff == 0:
            match_reasons.append("Enerji səviyyəsi həyat ritminizlə 100% üst-üstə düşür")

        # 4. Living space compatibility
        if answers.living_space == "apartment":
            if pet.size == "Large" and pet.energy_level >= 4:
                score -= 20
            elif pet.size in ["Small", "Medium"] or pet.species in ["cat", "rabbit", "bird"]:
                score += 10
                match_reasons.append("Mənzil şəraitində yaşamağa tam adaptasiya olunub")
        elif answers.living_space in ["house_with_yard", "countryside"]:
            if pet.energy_level >= 4 or pet.size == "Large":
                score += 10
                match_reasons.append("Həyətli ev və açıq sahə üçün ideal aktivlikdədir")

        # 5. Children safety check
        if answers.has_children:
            if pet.good_with_children:
                score += 15
                match_reasons.append("Uşaqlarla çox mehriban və səbirlidir")
            else:
                score -= 40

        # 6. Compatibility with existing pets
        if answers.has_other_pets:
            if pet.good_with_other_pets:
                score += 15
                match_reasons.append("Evdəki digər heyvanlarla dinc yanaşı yaşaya bilir")
            else:
                score -= 35

        # Normalize score between 25% and 99%
        final_score = max(25, min(99, score))

        results.append({
            "pet_id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "gender": pet.gender,
            "age_years": pet.age_years,
            "size": pet.size,
            "photo_url": pet.photo_url,
            "personality": pet.personality,
            "status": pet.status,
            "compatibility_score": final_score,
            "match_reasons": match_reasons[:3]
        })

    # Sort descending by compatibility score
    results.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return results[:8]  # Return top 8 best matches
