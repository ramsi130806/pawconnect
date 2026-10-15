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
