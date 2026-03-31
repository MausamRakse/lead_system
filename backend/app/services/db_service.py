import logging
from sqlalchemy.orm import Session
from app.models.lead import Lead

logger = logging.getLogger(__name__)

def save_or_update_lead(db: Session, data: dict) -> Lead:
    """Save a lead to the database or update it if it already exists (by email)."""
    email = data.get("email")
    if not email or email in ["", "Not available"]:
        logger.warning("Attempted to save lead without valid email: %s", data.get("name"))
        return None

    # Check for existing lead by email
    existing_lead = db.query(Lead).filter(Lead.email == email).first()

    if existing_lead:
        # Update existing record
        for key, value in data.items():
            if key == "id":
                continue # Skip ID as it is a string hash from Apollo, but an integer in our DB
            if hasattr(existing_lead, key) and value is not None:
                setattr(existing_lead, key, value)
        logger.info("Updated existing lead: %s", email)
    else:
        # Create new record
        existing_lead = Lead(
            name          = data.get("name"),
            title         = data.get("title"),
            company_name  = data.get("company_name") or data.get("company"),
            about_company = data.get("about_company"),
            email         = email,
            phone         = data.get("phone"),
            linkedin_url  = data.get("linkedin_url"),
            industry      = data.get("industry"),
            country       = data.get("country"),
            state         = data.get("state"),
            city          = data.get("city"),
            company_size  = data.get("company_size"),
        )
        db.add(existing_lead)
        logger.info("Created new lead: %s", email)

    try:
        db.commit()
        db.refresh(existing_lead)
    except Exception as e:
        db.rollback()
        logger.error("Failed to persist lead %s: %s", email, str(e))
        return None

    return existing_lead
