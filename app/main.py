import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.seed import seed_database
from app.routers import pages, api_pets, api_adoptions, api_vaccines, api_quiz, api_shelters

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite / PostgreSQL tables and seed realistic dataset
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

app = FastAPI(
    title="PawConnect - Animal Adoption & Shelter Management System",
    description="Official Software Project for Atlântia International STEM Olympiad (SW01: Software Projects). Consolidates pet profiles, digital vaccine passports, and adoption applications.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for open API consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include Routers
app.include_router(pages.router)
app.include_router(api_pets.router)
app.include_router(api_adoptions.router)
app.include_router(api_vaccines.router)
app.include_router(api_quiz.router)
app.include_router(api_shelters.router)

@app.get("/health", tags=["System"])
def health_check():
    """Healthcheck endpoint for Render / Railway zero-downtime deployment."""
    return {"status": "healthy", "project": "PawConnect", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
