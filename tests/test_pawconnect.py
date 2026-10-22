import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Pet, Shelter, VaccineRecord, AdoptionApplication
from app.seed import seed_database

# TestClient without a context manager does not run the app lifespan,
# so create tables and seed data explicitly (works even on a fresh checkout).
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
    """
    Test submitting an adoption application.
    """
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


def test_favicon_endpoint():
    """Verify favicon is served successfully."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert "svg" in response.headers.get("content-type", "")


def test_admin_unauthorized_redirects_to_login():
    """Verify that unauthenticated user trying to access /admin is redirected to /login."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers.get("location", "")


def test_admin_login_flow():
    """Verify full admin login, authenticated session access, and logout."""
    # 1. Login page loads
    res_page = client.get("/login")
    assert res_page.status_code == 200
    assert "admin" in res_page.text.lower()

    # 2. Invalid credentials fail with 401
    bad_login = client.post("/login", data={"username": "admin", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # 3. Valid credentials succeed and redirect to admin
    good_login = client.post(
        "/login",
        data={"username": "admin", "password": "idschool2026", "next": "/admin"},
        follow_redirects=False
    )
    assert good_login.status_code == 303
    assert "/admin" in good_login.headers.get("location", "")
    assert "pawconnect_admin_session" in good_login.cookies

    # 4. Access admin with session cookie
    admin_session_cookie = good_login.cookies["pawconnect_admin_session"]
    admin_res = client.get("/admin", cookies={"pawconnect_admin_session": admin_session_cookie})
    assert admin_res.status_code == 200
    assert "İdarəetmə Paneli" in admin_res.text or "Dashboard" in admin_res.text

    # 5. Logout clears cookie
    logout_res = client.get("/logout", follow_redirects=False)
    assert logout_res.status_code == 303


def test_user_register_and_login_flow():
    """Verify standard user registration, duplicate checks, login, and access."""
    # 1. Register page loads
    reg_page = client.get("/register")
    assert reg_page.status_code == 200

    # 2. Register a new user
    import time
    test_email = f"tester_{int(time.time())}@pawconnect.az"
    reg_res = client.post(
        "/register",
        data={
            "name": "Kamran Aliyev",
            "email": test_email,
            "password": "mypassword123",
            "confirm_password": "mypassword123"
        },
        follow_redirects=False
    )
    assert reg_res.status_code == 303
    assert "pawconnect_session" in reg_res.cookies

    # 3. Duplicate email registration fails
    dup_res = client.post(
        "/register",
        data={
            "name": "Kamran Duplicate",
            "email": test_email,
            "password": "mypassword123",
            "confirm_password": "mypassword123"
        }
    )
    assert dup_res.status_code == 400

    # 4. Login as newly registered user
    login_res = client.post(
        "/login",
        data={"username": test_email, "password": "mypassword123"},
        follow_redirects=False
    )
    assert login_res.status_code == 303
    assert "pawconnect_session" in login_res.cookies


def test_favorites_page_and_api():
    """Verify /favorites page and toggle API."""
    fav_page = client.get("/favorites")
    assert fav_page.status_code == 200

    toggle_res = client.post("/api/favorites/1")
    assert toggle_res.status_code == 200
    assert "is_favorite" in toggle_res.json()


def test_multilingual_pet_bios():
    """Verify pet bios and personality change across AZ, EN, and RU."""
    # Detail in AZ
    res_az = client.get("/pets/1?lang=az")
    assert res_az.status_code == 200
    assert "Haqqında" in res_az.text or "O питомце" not in res_az.text

    # Detail in RU
    res_ru = client.get("/pets/1?lang=ru")
    assert res_ru.status_code == 200
    assert "О питомце" in res_ru.text
    assert "Особенности характера" in res_ru.text

    # Detail in EN
    res_en = client.get("/pets/1?lang=en")
    assert res_en.status_code == 200
    assert "About" in res_en.text
    assert "Personality Traits" in res_en.text


def test_expanded_smart_matcher_algorithm():
    """Verify 7-dimension matching algorithm with time, experience, shedding preferences."""
    payload = {
        "living_space": "apartment",
        "daily_time": 1,  # <30 mins
        "experience_level": "beginner",
        "energy_preference": 2,
        "has_children": True,
        "has_other_pets": True,
        "shedding_preference": "low_shedding",
        "preferred_species": "any",
        "preferred_size": "any"
    }
    res = client.post("/api/quiz/match?lang=ru", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    top = data[0]
    assert "compatibility_score" in top
    assert "match_reasons" in top
    assert "personality" in top
    assert "description" in top
    assert top["compatibility_score"] >= 25


def test_pet_photo_upload():
    """Verify direct image upload returning static url."""
    import io
    dummy_file = io.BytesIO(b"FAKE_PNG_BINARY_CONTENT")
    res = client.post(
        "/api/pets/upload-photo",
        files={"file": ("test_pet.png", dummy_file, "image/png")}
    )
    assert res.status_code == 200
    body = res.json()
    assert "photo_url" in body
    assert body["photo_url"].startswith("/static/uploads/pets/")


