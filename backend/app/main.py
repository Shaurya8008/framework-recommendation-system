from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base, SessionLocal
from app.db.seed import seed_frameworks
from app.routers import profiles, frameworks, recommend, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and auto-seed catalog on startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_frameworks(db)
        print(f"[Startup] Verified {count} frameworks in catalog.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="FrameworkFit API",
    description="Sustainability Framework Recommendation System Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration (Lovable React/Vite app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(frameworks.router)
app.include_router(recommend.router)
app.include_router(documents.router)


@app.get("/", tags=["health"])
def healthcheck():
    return {"status": "ok", "service": "FrameworkFit API", "version": "1.0.0"}

