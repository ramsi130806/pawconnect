import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Pet, Shelter, VaccineRecord, AdoptionApplication, User, Favorite
from app.seed import seed_database

seed_database()
client = TestClient(app)

def test_health_check():
    """Verify backend health endpoint is active and healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "PawConnect"


def test_home_page():
    """Verify that home page loads with status 200 and renders app name."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PawConnect" in response.text


def test_pets_catalog():
    """Verify pet catalog listing and filters work."""
    response = client.get("/pets?species=dog")
    assert response.status_code == 200
    assert "🐶" in response.text or "dog" in response.text.lower()


def test_pet_detail_page():
    """Verify pet profile and medical passport history load."""
    response = client.get("/pets/1")
    assert response.status_code == 200
    assert "Tibbi Pasport" in response.text or "Medical Passport" in response.text


def test_smart_matcher_algorithm():
    """
    Test the Smart Pet Matcher algorithmic scoring (Input -> Processing -> Output).
    """
    payload = {
        "living_space": "apartment",
        "energy_preference": 2,
        "has_children": True,
        "has_other_pets": True,
        "preferred_species": "cat",
        "preferred_size": "Small"
    }
    response = client.post("/api/quiz/match", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    top_match = results[0]
    assert "compatibility_score" in top_match
    assert top_match["compatibility_score"] >= 50
    assert len(top_match["match_reasons"]) > 0


def test_submit_adoption_application():
    """Test submitting an adoption application."""
    payload = {
        "pet_id": 1,
        "applicant_name": "Test İştirakçı",
        "applicant_email": "test@pawconnect.az",
        "applicant_phone": "+994 (50) 111-22-33",
        "applicant_city": "Bakı",
        "living_space": "apartment",
        "has_other_pets": False,
        "has_children": True,
        "experience_level": "intermediate",
        "hours_alone_per_day": 3,
        "message": "STEM Olimpiadası sınaq müraciəti"
    }
    response = client.post("/api/adoptions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["applicant_name"] == "Test İştirakçı"
    assert data["status"] == "pending"


def test_shelters_api():
    """Verify accredited shelters API."""
    response = client.get("/api/shelters")
    assert response.status_code == 200
    shelters = response.json()
    assert len(shelters) >= 4


def test_admin_unauthorized_redirects_to_login():
    """Verify non-authenticated user or guest cannot access /admin and gets redirected to login."""
    res = client.get("/admin", follow_redirects=False)
    assert res.status_code == 303
    assert "/login" in res.headers.get("location", "")


def test_admin_login_flow():
    """Verify admin login with username 'admin' and password 'idschool'."""
    # Bad credentials fail
    bad_login = client.post("/login", data={"username": "admin", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # Correct admin credentials
    good_login = client.post(
        "/login",
        data={"username": "admin", "password": "idschool", "next": "/admin"},
        follow_redirects=False
    )
    assert good_login.status_code == 303
    assert "/admin" in good_login.headers.get("location", "")
    assert "pawconnect_session" in good_login.cookies

    # Access /admin with admin session
    admin_cookie = good_login.cookies["pawconnect_session"]
    admin_page = client.get("/admin", cookies={"pawconnect_session": admin_cookie})
    assert admin_page.status_code == 200
    assert "İdarəetmə Paneli" in admin_page.text or "Dashboard" in admin_page.text


def test_user_registration_and_isolation():
    """Verify standard user can register, login, access pets, but cannot access /admin."""
    unique_email = f"user_{int(time.time())}@pawconnect.az"

    # 1. Register new user
    reg_res = client.post(
        "/register",
        data={
            "name": "Aysel Məmmədova",
            "email": unique_email,
            "password": "userpass123",
            "confirm_password": "userpass123"
        },
        follow_redirects=False
    )
    assert reg_res.status_code == 303
    assert "pawconnect_session" in reg_res.cookies
    user_cookie = reg_res.cookies["pawconnect_session"]

    # 2. User can access pets & favorites
    pets_res = client.get("/pets", cookies={"pawconnect_session": user_cookie})
    assert pets_res.status_code == 200

    favs_res = client.get("/favorites", cookies={"pawconnect_session": user_cookie})
    assert favs_res.status_code == 200

    # 3. User CANNOT access /admin (redirects to /login)
    admin_attempt = client.get("/admin", cookies={"pawconnect_session": user_cookie}, follow_redirects=False)
    assert admin_attempt.status_code == 303
    assert "/login" in admin_attempt.headers.get("location", "")


def test_favorites_api():
    """Verify toggle favorite API."""
    fav_res = client.post("/api/favorites/1")
    assert fav_res.status_code == 200
    assert "is_favorite" in fav_res.json()


def test_multilingual_localization():
    """Verify that pet descriptions and personality traits translate properly across AZ, EN, and RU."""
    # Azerbaijani
    res_az = client.get("/pets/1?lang=az")
    assert res_az.status_code == 200
    assert "Haqqında" in res_az.text

    # Russian
    res_ru = client.get("/pets/1?lang=ru")
    assert res_ru.status_code == 200
    assert "О питомце" in res_ru.text
    assert "Особенности характера" in res_ru.text
    assert "немецкой овчарки" in res_ru.text or "Барон" in res_ru.text

    # English
    res_en = client.get("/pets/1?lang=en")
    assert res_en.status_code == 200
    assert "About" in res_en.text
    assert "German Shepherd" in res_en.text or "Baron" in res_en.text
