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
    },
    "time_match": {
        "az": "Gündəlik vaxt cədvəliniz və gəzinti rejiminizlə uyğundur",
        "en": "Matches your daily time availability and routine",
        "ru": "Идеально соответствует вашему свободному времени"
    },
    "exp_match": {
        "az": "Təcrübə səviyyəniz üçün asan və rahat qulluq olunan dostdur",
        "en": "Great companion for your experience level",
        "ru": "Прекрасно подходит для вашего уровня опыта"
    },
    "shed_match": {
        "az": "Tük tökülməsi və təmizlik tələblərinizi qarşılayır",
        "en": "Matches your coat grooming & shedding preferences",
        "ru": "Подходит по требованиям к уходу за шерстью"
    }
}

def get_reason(key: str, lang: str) -> str:
    lang = (lang or "az").lower()
    if lang not in ["az", "en", "ru"]:
        lang = "az"
    return REASONS_I18N.get(key, {}).get(lang, REASONS_I18N.get(key, {}).get("az", ""))

@router.post("/match")
def calculate_matches(
    answers: QuizAnswers,
    lang: str = Query("az"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Intelligent 7-Dimension Compatibility Algorithm.
    Ranks available shelter pets based on applicant's home space, time commitment,
    pet care experience, energy levels, children, other pets, and shedding tolerance.
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
                score -= 35

        # 2. Size preference
        if answers.preferred_size and answers.preferred_size != "any":
            if pet.size == answers.preferred_size:
                score += 10
                match_reasons.append(get_reason("size_match", lang))
            else:
                score -= 10

        # 3. Energy level proximity (1 to 5)
        energy_diff = abs(pet.energy_level - answers.energy_preference)
        score -= energy_diff * 7
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

        # 5. Daily Time Commitment (1: <30m, 2: 30-60m, 3: 1-2h, 4: 2h+)
        if answers.daily_time:
            if answers.daily_time == 1:  # Low time
                if pet.species in ["cat", "rabbit", "bird"] or pet.energy_level <= 2:
                    score += 12
                    match_reasons.append(get_reason("time_match", lang))
                else:
                    score -= 15
            elif answers.daily_time in [3, 4]:  # High time
                if pet.energy_level >= 4:
                    score += 12
                    match_reasons.append(get_reason("time_match", lang))

        # 6. Experience Level (beginner, intermediate, experienced)
        if answers.experience_level == "beginner":
            if pet.house_trained and pet.good_with_children and pet.energy_level <= 3:
                score += 10
                match_reasons.append(get_reason("exp_match", lang))
            elif pet.energy_level >= 5 or not pet.house_trained:
                score -= 12

        # 7. Shedding / Allergy Sensitivity
        if answers.shedding_preference == "low_shedding":
            if pet.species in ["bird", "rabbit"] or pet.size == "Small" or "qısa" in pet.breed.lower() or "short" in pet.breed.lower():
                score += 12
                match_reasons.append(get_reason("shed_match", lang))
            elif "samoyed" in pet.breed.lower() or "retriever" in pet.breed.lower():
                score -= 15

        # 8. Children safety check
        if answers.has_children:
            if pet.good_with_children:
                score += 15
                match_reasons.append(get_reason("kids_match", lang))
            else:
                score -= 40

        # 9. Other pets check
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
