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
    """Verify favorites require a signed-in user session and work when authenticated."""
    client.cookies.clear()
    # Guest request must be rejected (401 on API, 303 redirect on page)
    guest_api = client.post("/api/favorites/1")
    assert guest_api.status_code == 401
    guest_page = client.get("/favorites", follow_redirects=False)
    assert guest_page.status_code == 303
    assert "/login" in guest_page.headers.get("location", "")

    # Authenticated user can toggle favorite
    login_res = client.post(
        "/login",
        data={"username": "user@pawconnect.az", "password": "user123456"},
        follow_redirects=False
    )
    user_cookie = login_res.cookies["pawconnect_session"]
    fav_res = client.post("/api/favorites/1", cookies={"pawconnect_session": user_cookie})
    assert fav_res.status_code == 200
    assert "is_favorite" in fav_res.json()
    assert fav_res.json()["authenticated"] is True


def test_my_applications_page_and_overdue_vaccines():
    """Verify My Applications page shows user adoption status and overdue vaccines exist."""
    client.cookies.clear()
    # Guest redirects to login
    guest_res = client.get("/my-applications", follow_redirects=False)
    assert guest_res.status_code == 303
    assert "/login" in guest_res.headers.get("location", "")

    # Signed-in user can submit an application and see it on /my-applications
    login_res = client.post(
        "/login",
        data={"username": "user@pawconnect.az", "password": "user123456"},
        follow_redirects=False
    )
    user_cookie = login_res.cookies["pawconnect_session"]

    app_payload = {
        "pet_id": 2,
        "applicant_name": "Nuran Əliyev",
        "applicant_email": "user@pawconnect.az",
        "applicant_phone": "+994 (50) 222-33-44",
        "applicant_city": "Bakı",
        "living_space": "apartment",
        "has_other_pets": False,
        "has_children": True,
        "experience_level": "intermediate",
        "hours_alone_per_day": 3,
        "message": "Müraciət statusunun yoxlanılması"
    }
    post_res = client.post("/api/adoptions", json=app_payload, cookies={"pawconnect_session": user_cookie})
    assert post_res.status_code == 201

    my_apps_en = client.get("/my-applications?lang=en", cookies={"pawconnect_session": user_cookie})
    assert my_apps_en.status_code == 200
    assert "My Adoption Applications" in my_apps_en.text
    assert "Luna" in my_apps_en.text

    # Overdue vaccines endpoint and pet passport alert
    overdue_res = client.get("/api/vaccines/alerts/overdue")
    assert overdue_res.status_code == 200
    assert len(overdue_res.json()) >= 5


def test_multilingual_localization():
    """Verify that UI, breeds, shelters, vaccines, pet descriptions and traits translate across AZ, EN, and RU."""
    # Azerbaijani
    res_az = client.get("/pets/1?lang=az")
    assert res_az.status_code == 200
    assert "Haqqında" in res_az.text

    # Russian
    res_ru = client.get("/pets/1?lang=ru")
    assert res_ru.status_code == 200
    assert "О питомце" in res_ru.text
    assert "Особенности характера" in res_ru.text
    assert "Немецкая овчарка" in res_ru.text
    assert "Бакинский центр спасения животных" in res_ru.text

    # English (including home page & previously untranslated pets like Zümrüd #10)
    res_en = client.get("/pets/1?lang=en")
    assert res_en.status_code == 200
    assert "About" in res_en.text
    assert "German Shepherd (Mix)" in res_en.text
    assert "Baku Animal Rescue Center" in res_en.text

    home_en = client.get("/?lang=en")
    assert home_en.status_code == 200
    assert "Verified Shelters" in home_en.text
    assert "Yoxlanmış Sığınacaqlar" not in home_en.text
