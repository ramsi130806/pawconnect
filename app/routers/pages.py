from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Request, Depends, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models import Pet, Shelter, VaccineRecord, AdoptionApplication, User, Favorite
from app.i18n import get_text, translate_personality_traits, translate_data, translate_species, translate_size
from app.auth import (
    check_admin_credentials,
    generate_session_token,
    get_authenticated_user,
    is_admin_authenticated,
    hash_password,
    verify_password,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE
)

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

# Register global template helpers
templates.env.globals["translate_traits"] = translate_personality_traits
# Database content translation filters, e.g. {{ pet.breed|tr(lang) }}
templates.env.filters["tr"] = translate_data
templates.env.filters["species_name"] = translate_species
templates.env.filters["size_name"] = translate_size


def get_locale(request: Request, lang: Optional[str] = None) -> str:
    """Determine the active UI language: query param > cookie > default 'az'."""
    if lang in ["az", "en", "ru"]:
        return lang
    cookie_lang = request.cookies.get("preferred_lang")
    if cookie_lang in ["az", "en", "ru"]:
        return cookie_lang
    return "az"


def has_personal_account(user: Optional[dict]) -> bool:
    """True when the session belongs to a registered user account (favorites / applications)."""
    return bool(user and user.get("user_id") and user.get("user_id") > 0)


def with_lang(url: str, lang: str) -> str:
    """Append ?lang= / &lang= to a URL safely."""
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}lang={lang}"


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

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
            "user": user,
            "is_admin": is_admin_authenticated(request),
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
    user = get_authenticated_user(request)

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
            "user": user,
            "is_admin": is_admin_authenticated(request),
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
    user = get_authenticated_user(request)

    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        return HTMLResponse(content="<h1>Heyvan tapılmadı / Pet not found</h1>", status_code=404)

    vaccines = db.query(VaccineRecord).filter(VaccineRecord.pet_id == pet_id).order_by(VaccineRecord.administered_date.desc()).all()
    overdue_count = sum(1 for v in vaccines if v.computed_status == "overdue")

    # Signed-in account details (to prefill and link the adoption application)
    account = None
    if has_personal_account(user):
        account = db.query(User).filter(User.id == user["user_id"]).first()

    response = templates.TemplateResponse(
        request=request,
        name="pet_detail.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": user,
            "is_admin": is_admin_authenticated(request),
            "pet": pet,
            "vaccines": vaccines,
            "overdue_count": overdue_count,
            "account": account
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/match", response_class=HTMLResponse)
def quiz_page(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    response = templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": user,
            "is_admin": is_admin_authenticated(request)
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    response = templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": user,
            "is_admin": is_admin_authenticated(request)
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


# --- FAVORITES SYSTEM (available only for signed-in user accounts) ---
@router.get("/favorites", response_class=HTMLResponse)
def favorites_page(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    # Guests must sign in to their own account to use favorites
    if not has_personal_account(user):
        return RedirectResponse(url=f"/login?next=/favorites&lang={active_lang}", status_code=303)

    fav_records = db.query(Favorite).filter(Favorite.user_id == user["user_id"]).order_by(Favorite.created_at.desc()).all()
    fav_ids = [f.pet_id for f in fav_records]
    favorite_pets = db.query(Pet).filter(Pet.id.in_(fav_ids)).all() if fav_ids else []

    response = templates.TemplateResponse(
        request=request,
        name="favorites.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": user,
            "is_admin": is_admin_authenticated(request),
            "pets": favorite_pets
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.post("/api/favorites/{pet_id}")
def toggle_favorite(request: Request, pet_id: int, db: Session = Depends(get_db)):
    """Toggle a pet in the signed-in user's favorites. Guests receive 401."""
    user = get_authenticated_user(request)
    if not has_personal_account(user):
        return JSONResponse(status_code=401, content={"detail": "login_required", "authenticated": False})

    if not db.query(Pet.id).filter(Pet.id == pet_id).first():
        return JSONResponse(status_code=404, content={"detail": "Pet not found"})

    existing = db.query(Favorite).filter(Favorite.user_id == user["user_id"], Favorite.pet_id == pet_id).first()
    if existing:
        db.delete(existing)
        is_fav = False
    else:
        db.add(Favorite(user_id=user["user_id"], pet_id=pet_id))
        is_fav = True
    db.commit()

    count = db.query(Favorite).filter(Favorite.user_id == user["user_id"]).count()
    return {"pet_id": pet_id, "is_favorite": is_fav, "authenticated": True, "count": count}


@router.get("/api/favorites")
def get_user_favorites(request: Request, db: Session = Depends(get_db)):
    """Get list of favorite pet IDs for authenticated user."""
    user = get_authenticated_user(request)
    if not has_personal_account(user):
        return {"favorites": [], "authenticated": False}
    favs = db.query(Favorite.pet_id).filter(Favorite.user_id == user["user_id"]).all()
    return {"favorites": [f[0] for f in favs], "authenticated": True}


# --- MY APPLICATIONS (adoption request status tracking) ---
@router.get("/my-applications", response_class=HTMLResponse)
def my_applications_page(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    if not has_personal_account(user):
        return RedirectResponse(url=f"/login?next=/my-applications&lang={active_lang}", status_code=303)

    account = db.query(User).filter(User.id == user["user_id"]).first()
    filters = [AdoptionApplication.user_id == user["user_id"]]
    if account and account.email:
        # Also include applications sent earlier with the same e-mail address
        filters.append(func.lower(AdoptionApplication.applicant_email) == account.email.lower())

    applications = (
        db.query(AdoptionApplication)
        .filter(or_(*filters))
        .order_by(AdoptionApplication.created_at.desc())
        .all()
    )

    response = templates.TemplateResponse(
        request=request,
        name="my_applications.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": user,
            "is_admin": is_admin_authenticated(request),
            "applications": applications
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


# --- AUTHENTICATION & ACCESS CONTROL ---
@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    # STRICT ACCESS CONTROL: Only users with 'admin' role can view /admin
    if not is_admin_authenticated(request):
        return RedirectResponse(url=f"/login?next=/admin&lang={active_lang}", status_code=303)

    user = get_authenticated_user(request)
    pets = db.query(Pet).order_by(Pet.id.desc()).all()
    shelters = db.query(Shelter).all()
    applications = db.query(AdoptionApplication).order_by(AdoptionApplication.created_at.desc()).all()

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
            "user": user,
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


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: Optional[str] = None, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    if user:
        if user.get("role") == "admin":
            return RedirectResponse(url=f"/admin?lang={active_lang}", status_code=303)
        return RedirectResponse(url=f"/pets?lang={active_lang}", status_code=303)

    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": None,
            "is_admin": False,
            "next": next or "",
            "error": None
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    form = await request.form()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))
    next_url = str(form.get("next", "")).strip()

    # 1. Admin Login Check (admin / idschool)
    if check_admin_credentials(username, password):
        target = next_url if (next_url and next_url.startswith("/")) else "/admin"
        response = RedirectResponse(url=with_lang(target, active_lang), status_code=303)
        token = generate_session_token(role="admin", user_id=0, name="Admin")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/"
        )
        response.set_cookie(
            key="pawconnect_admin_session",
            value=token,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/"
        )
        response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
        return response

    # 2. Regular User Login Check (Email & Password)
    db_user = db.query(User).filter(User.email == username.lower()).first()
    if db_user and verify_password(password, db_user.password_hash):
        target = next_url if (next_url and next_url.startswith("/")) else "/pets"
        response = RedirectResponse(url=with_lang(target, active_lang), status_code=303)
        token = generate_session_token(role=db_user.role, user_id=db_user.id, name=db_user.name)
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

    # 3. Invalid credentials
    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": None,
            "is_admin": False,
            "next": next_url,
            "error": t.get("login_error_invalid", "İstifadəçi adı və ya şifrə yanlışdır. Yenidən cəhd edin.")
        },
        status_code=401
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)
    user = get_authenticated_user(request)

    if user:
        return RedirectResponse(url=f"/pets?lang={active_lang}", status_code=303)

    response = templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "lang": active_lang,
            "t": t,
            "user": None,
            "is_admin": False,
            "error": None
        }
    )
    response.set_cookie("preferred_lang", active_lang, max_age=30*86400)
    return response


@router.post("/register", response_class=HTMLResponse)
async def register_submit(request: Request, lang: Optional[str] = None, db: Session = Depends(get_db)):
    active_lang = get_locale(request, lang)
    t = get_text(active_lang)

    form = await request.form()
    name = str(form.get("name", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))
    confirm_password = str(form.get("confirm_password", ""))

    # Validation checks
    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "lang": active_lang,
                "t": t,
                "user": None,
                "is_admin": False,
                "error": t.get("register_error_short", "Şifrə ən azı 6 simvoldan ibarət olmalıdır.")
            },
            status_code=400
        )

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "lang": active_lang,
                "t": t,
                "user": None,
                "is_admin": False,
                "error": t.get("register_error_mismatch", "Şifrələr bir-biri ilə uyğun gəlmir.")
            },
            status_code=400
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "lang": active_lang,
                "t": t,
                "user": None,
                "is_admin": False,
                "error": t.get("register_error_exists", "Bu e-poçt ünvanı ilə artıq qeydiyyat mövcuddur.")
            },
            status_code=400
        )

    # Create new user
    new_user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Auto login upon registration
    response = RedirectResponse(url=f"/pets?lang={active_lang}", status_code=303)
    token = generate_session_token(role="user", user_id=new_user.id, name=new_user.name)
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


@router.get("/logout")
def logout(request: Request, lang: Optional[str] = None):
    active_lang = get_locale(request, lang)
    response = RedirectResponse(url=f"/?lang={active_lang}", status_code=303)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(key="pawconnect_admin_session", path="/")
    return response
