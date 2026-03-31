import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.lead import Lead

logger = logging.getLogger(__name__)


def save_leads_to_db(leads_data: list[dict], filters: dict) -> None:
    """Save a list of lead dicts to the database, skipping duplicates by email."""
    db: Session = SessionLocal()
    try:
        industry = filters.get("industry", "")
        country  = filters.get("location", "")
        state    = filters.get("state", "")
        city     = filters.get("city", "")

        company_size = filters.get("company_size", "")
        if not company_size and filters.get("company_size_min"):
            company_size = f"{filters.get('company_size_min')}-{filters.get('company_size_max')}"

        for l in leads_data:
            email = l.get("email", "")
            if email and email not in ("Not available", ""):
                existing = db.query(Lead).filter(Lead.email == email).first()
                if existing:
                    continue

            new_lead = Lead(
                name          = l.get("name", ""),
                title         = l.get("title", ""),
                company_name  = l.get("company", ""),
                about_company = l.get("about_company", ""),
                email         = email,
                phone         = l.get("phone", ""),
                linkedin_url  = l.get("linkedin_url", ""),
                industry      = industry,
                country       = country,
                state         = state,
                city          = city,
                company_size  = company_size,
            )
            db.add(new_lead)

        db.commit()
    except Exception as e:
        logger.error("DB save error: %s", e)
        db.rollback()
    finally:
        db.close()
