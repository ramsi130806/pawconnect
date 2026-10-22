from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pet
from app.schemas import QuizAnswers

router = APIRouter(prefix="/api/quiz", tags=["Smart Matcher Algorithm"])

REASONS_I18N = {
    "species_match": {
        "az": "Tələb olunan heyvan növünə tam uyğundur",
        "en": "Matches your preferred animal species",
        "ru": "Полностью соответствует выбранному виду питомца"
    },
    "size_match": {
        "az": "Ölçü seçiminizi qarşılayır",
        "en": "Meets your preferred size criteria",
        "ru": "Подходит по желаемому размеру"
    },
    "energy_match": {
        "az": "Enerji səviyyəsi həyat ritminizlə 100% üst-üstə düşür",
        "en": "Energy level perfectly aligns with your lifestyle",
        "ru": "Уровень активности идеально подходит вашему ритму"
    },
    "apt_match": {
        "az": "Mənzil şəraitində yaşamağa tam adaptasiya olunub",
        "en": "Well-adapted for apartment living",
        "ru": "Отлично адаптирован для проживания в квартире"
    },
    "yard_match": {
        "az": "Həyətli ev və açıq sahə üçün ideal aktivlikdədir",
        "en": "Ideal energy and size for a house with yard",
        "ru": "Идеальный уровень активности для дома с двором"
    },
    "kids_match": {
        "az": "Uşaqlarla çox mehriban və səbirlidir",
        "en": "Very gentle and patient with children",
        "ru": "Очень дружелюбен и терпелив с детьми"
    },
    "pets_match": {
        "az": "Evdəki digər heyvanlarla dinc yanaşı yaşaya bilir",
        "en": "Friendly and peaceful with other household pets",
        "ru": "Мирно уживается с другими питомцами"
    }
}

def get_reason(key: str, lang: str) -> str:
    lang = lang.lower() if lang in ["az", "en", "ru"] else "az"
    return REASONS_I18N.get(key, {}).get(lang, REASONS_I18N[key]["az"])

@router.post("/match")
def calculate_matches(
    answers: QuizAnswers,
    lang: str = Query("az"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
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
                match_reasons.append(get_reason("species_match", lang))
            else:
                score -= 30

        # 2. Size preference
        if answers.preferred_size and answers.preferred_size != "any":
            if pet.size == answers.preferred_size:
                score += 10
                match_reasons.append(get_reason("size_match", lang))
            else:
                score -= 10

        # 3. Energy level proximity (1 to 5)
        energy_diff = abs(pet.energy_level - answers.energy_preference)
        energy_penalty = energy_diff * 8
        score -= energy_penalty
        if energy_diff == 0:
            match_reasons.append(get_reason("energy_match", lang))

        # 4. Living space compatibility
        if answers.living_space == "apartment":
            if pet.size == "Large" and pet.energy_level >= 4:
                score -= 20
            elif pet.size in ["Small", "Medium"] or pet.species in ["cat", "rabbit", "bird"]:
                score += 10
                match_reasons.append(get_reason("apt_match", lang))
        elif answers.living_space in ["house_with_yard", "countryside"]:
            if pet.energy_level >= 4 or pet.size == "Large":
                score += 10
                match_reasons.append(get_reason("yard_match", lang))

        # 5. Children safety check
        if answers.has_children:
            if pet.good_with_children:
                score += 15
                match_reasons.append(get_reason("kids_match", lang))
            else:
                score -= 40

        # 6. Compatibility with existing pets
        if answers.has_other_pets:
            if pet.good_with_other_pets:
                score += 15
                match_reasons.append(get_reason("pets_match", lang))
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
            "personality": pet.get_personality(lang),
            "description": pet.get_description(lang),
            "status": pet.status,
            "compatibility_score": final_score,
            "match_reasons": match_reasons[:3]
        })

    # Sort descending by compatibility score
    results.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return results[:8]
