from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lead import Lead

router = APIRouter(tags=["db-leads"])


def _lead_to_dict(lead: Lead) -> dict:
    return {
        "id":           lead.id,
        "name":         lead.name,
        "title":        lead.title,
        "company_name": lead.company_name,
        "about_company": lead.about_company,
        "email":        lead.email,
        "phone":        lead.phone,
        "linkedin_url": lead.linkedin_url,
        "industry":     lead.industry,
        "country":      lead.country,
        "state":        lead.state,
        "city":         lead.city,
        "company_size": lead.company_size,
        "created_at":   lead.created_at.isoformat() if lead.created_at else None,
        "updated_at":   lead.updated_at.isoformat() if lead.updated_at else None,
    }


@router.get("/api/db-leads")
def get_db_leads(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Lead)
    if industry:
        query = query.filter(Lead.industry.ilike(f"%{industry}%"))
    if country:
        query = query.filter(Lead.country.ilike(f"%{country}%"))
    leads = query.offset(skip).limit(limit).all()
    return {"leads": [_lead_to_dict(l) for l in leads], "count": len(leads)}


@router.get("/api/db-leads/{lead_id}")
def get_db_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return _lead_to_dict(lead)


@router.post("/api/db-leads")
def create_db_lead(lead_data: dict, db: Session = Depends(get_db)):
    new_lead = Lead(
        name          = lead_data.get("name"),
        title         = lead_data.get("title"),
        company_name  = lead_data.get("company_name"),
        about_company = lead_data.get("about_company"),
        email         = lead_data.get("email"),
        phone         = lead_data.get("phone"),
        linkedin_url  = lead_data.get("linkedin_url"),
        industry      = lead_data.get("industry"),
        country       = lead_data.get("country"),
        state         = lead_data.get("state"),
        city          = lead_data.get("city"),
        company_size  = lead_data.get("company_size"),
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"id": new_lead.id, "name": new_lead.name}


@router.put("/api/db-leads/{lead_id}")
def update_db_lead(lead_id: int, lead_data: dict, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for key, value in lead_data.items():
        if hasattr(lead, key):
            setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return {"id": lead.id, "status": "updated"}


@router.delete("/api/db-leads/{lead_id}")
def delete_db_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"detail": "Lead deleted"}
