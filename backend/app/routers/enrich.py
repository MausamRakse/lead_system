import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.lead import EnrichRequest
from app.config import settings
from app.database import get_db
from app.services.db_service import save_or_update_lead
from utils.extractors import extract_email, extract_phone

logger = logging.getLogger(__name__)
router = APIRouter(tags=["enrich"])

APOLLO_ENRICH_URL = "https://api.apollo.io/api/v1/people/match"


@router.post("/api/enrich-lead")
async def enrich_lead(req: EnrichRequest, db: Session = Depends(get_db)):
    api_key = settings.APOLLO_API_KEY
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type":  "application/json",
        "accept":        "application/json",
        "X-Api-Key":     api_key,
    }
    payload = {
        "id":                     req.person_id,
        "reveal_personal_emails": True,
        "reveal_phone_number":    False,
        "webhook_url":            settings.WEBHOOK_URL,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(APOLLO_ENRICH_URL, headers=headers, json=payload, timeout=20.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Apollo API error: {response.text}",
                )

            person = response.json().get("person", {}) or {}
            org    = person.get("organization", {}) or {}

            logger.info("Enrich result — email: %s, phone: %s", extract_email(person), extract_phone(person))

            lead_info = {
                "name":               f"{person.get('first_name', '')} {person.get('last_name', '')}".strip() or "Unknown",
                "first_name":         person.get("first_name", ""),
                "last_name":          person.get("last_name", ""),
                "title":              person.get("title", ""),
                "company_name":       org.get("name", "Unknown Company"),
                "email":              extract_email(person),
                "phone":              extract_phone(person),
                "linkedin_url":       person.get("linkedin_url", ""),
                "employment_history": person.get("employment_history", []),
                "country":            person.get("country") or org.get("country") or "",
                "state":              person.get("state") or org.get("state") or "",
                "city":               person.get("city") or org.get("city") or "",
                "company_size":       str(org.get("estimated_num_employees") or org.get("employee_count") or ""),
                "industry":           org.get("industry") or person.get("industry") or "",
            }

            # Automate database push
            save_or_update_lead(db, lead_info)

            return lead_info
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
