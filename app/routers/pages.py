from typing import Optional
from datetime import date
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Pet, Shelter, VaccineRecord, AdoptionApplication
from app.i18n import get_text
from app.auth import (
    is_admin_authenticated,
    check_admin_credentials,
    generate_session_token,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE
)

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
    is_admin = is_admin_authenticated(request)

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
            "is_admin": is_admin,
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
    is_admin = is_admin_authenticated(request)

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
            "is_admin": is_admin,
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
    is_admin = is_admin_authenticated(request)

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
            "is_admin": is_admin,
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
    is_admin = is_admin_authenticated(request)

    response = templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "lang": active_lang,
            "t": t,
            "is_admin": is_admin
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    # Protect admin dashboard - only admin can see
    if not is_admin_authenticated(request):
        return RedirectResponse(url=f"/login?next=/admin&lang={active_lang}", status_code=303)

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
            "is_admin": True,
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
    is_admin = is_admin_authenticated(request)

    response = templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "lang": active_lang,
            "t": t,
            "is_admin": is_admin
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, lang: Optional[str] = None, next: Optional[str] = "/admin"):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    # If already logged in, redirect straight to admin or next url
    if is_admin_authenticated(request):
        target = next if (next and next.startswith("/")) else "/admin"
        return RedirectResponse(url=f"{target}?lang={active_lang}", status_code=303)

    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "lang": active_lang,
            "t": t,
            "is_admin": False,
            "next": next or "/admin",
            "error": None
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    form = await request.form()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))
    next_url = str(form.get("next", "/admin"))
    if not next_url.startswith("/"):
        next_url = "/admin"

    if check_admin_credentials(username, password):
        target_url = f"{next_url}?lang={active_lang}"
        response = RedirectResponse(url=target_url, status_code=303)
        token = generate_session_token()
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/"
        )
        response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
        return response

    # Invalid credentials
    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "lang": active_lang,
            "t": t,
            "is_admin": False,
            "next": next_url,
            "error": t.get("login_error_invalid", "İstifadəçi adı və ya şifrə yanlışdır. Yenidən cəhd edin.")
        },
        status_code=401
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/logout")
def logout(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    response = RedirectResponse(url=f"/?lang={active_lang}", status_code=303)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return response
