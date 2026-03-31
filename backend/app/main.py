import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models.lead import Lead  # noqa: F401  (needed for metadata.create_all)
from app.database import Base
from app.routers import leads, enrich, geo, export, db_leads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Apollo Lead Extraction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(enrich.router)
app.include_router(geo.router)
app.include_router(export.router)
app.include_router(db_leads.router)

# On Render, rootDir=backend so the process CWD is `backend/`.
# os.getcwd() + "/../frontend" resolves to the repo-root `frontend/` directory.
# Set the FRONTEND_DIR environment variable to override this for any custom layout.
_default_frontend = os.path.join(os.getcwd(), "..", "frontend")
FRONTEND_DIR = os.path.abspath(os.environ.get("FRONTEND_DIR", _default_frontend))

logging.getLogger(__name__).info("Serving frontend from: %s", FRONTEND_DIR)

# Mount the frontend directory at root. html=True automatically serves index.html
# for unknown routes, enabling client-side navigation to work correctly.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
