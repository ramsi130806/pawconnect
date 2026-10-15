from typing import Optional
from datetime import date
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Pet, Shelter, VaccineRecord, AdoptionApplication
from app.i18n import get_text

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

def get_locale(request: Request, lang: Optional[str] = None) -> str:
    if lang in ["az", "en", "ru"]:
        return lang
    cookie_lang = request.cookies.get("preferred_lang")
    if cookie_lang in ["az", "en", "ru"]:
        return cookie_lang
    return "az"


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    total_pets = db.query(Pet).count()
    total_shelters = db.query(Shelter).count()
    total_adopted = db.query(Pet).filter(Pet.status == "adopted").count()
    featured_pets = db.query(Pet).filter(Pet.status == "available").limit(6).all()

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "lang": active_lang,
            "t": t,
            "total_pets": total_pets,
            "total_shelters": total_shelters,
            "total_adopted": total_adopted + 12,
            "featured_pets": featured_pets
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/pets", response_class=HTMLResponse)
def pets_catalog(
    request: Request,
    lang: Optional[str] = None,
    species: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    query = db.query(Pet)
    if species and species != "all":
        query = query.filter(Pet.species == species.lower())
    if size and size != "all":
        query = query.filter(Pet.size == size)
    if gender and gender != "all":
        query = query.filter(Pet.gender == gender)
    if status and status != "all":
        query = query.filter(Pet.status == status)
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

    pets = query.order_by(Pet.id.asc()).all()

    response = templates.TemplateResponse(
        request=request,
        name="pets.html",
        context={
            "lang": active_lang,
            "t": t,
            "pets": pets,
            "species": species or "all",
            "size": size or "all",
            "gender": gender or "all",
            "status": status or "all",
            "q": q or ""
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/pets/{pet_id}", response_class=HTMLResponse)
def pet_detail(request: Request, pet_id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        return HTMLResponse(content="<h1>Heyvan tapılmadı / Pet not found</h1>", status_code=404)

    vaccines = db.query(VaccineRecord).filter(VaccineRecord.pet_id == pet_id).order_by(VaccineRecord.administered_date.desc()).all()

    response = templates.TemplateResponse(
        request=request,
        name="pet_detail.html",
        context={
            "lang": active_lang,
            "t": t,
            "pet": pet,
            "vaccines": vaccines
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/match", response_class=HTMLResponse)
def quiz_page(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    response = templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "lang": active_lang,
            "t": t
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    pets = db.query(Pet).order_by(Pet.id.desc()).all()
    shelters = db.query(Shelter).all()
    applications = db.query(AdoptionApplication).order_by(AdoptionApplication.created_at.desc()).all()

    # Metrics
    total_pets = len(pets)
    pending_apps = sum(1 for a in applications if a.status in ["pending", "reviewing"])
    adopted_pets = sum(1 for p in pets if p.status == "adopted")
    overdue_vaxes = db.query(VaccineRecord).filter(
        VaccineRecord.next_due_date != None,
        VaccineRecord.next_due_date < date.today()
    ).count()

    response = templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "lang": active_lang,
            "t": t,
            "pets": pets,
            "shelters": shelters,
            "applications": applications,
            "total_pets": total_pets,
            "pending_apps": pending_apps,
            "adopted_pets": adopted_pets,
            "overdue_vaxes": overdue_vaxes
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    response = templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "lang": active_lang,
            "t": t
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response
