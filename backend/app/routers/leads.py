import re
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.lead import LeadRequest, AISearchRequest
from app.services.apollo import fetch_apollo_leads
from app.database import get_db
from app.services.db_service import save_or_update_lead

logger = logging.getLogger(__name__)
router = APIRouter(tags=["leads"])


@router.post("/api/leads")
async def get_leads(req: LeadRequest, db: Session = Depends(get_db)):
    result = await fetch_apollo_leads(req.model_dump())
    
    # Automate database push for all extracted leads
    if "leads" in result:
        for lead_data in result["leads"]:
            # Merge request filters for more accurate location/size
            lead_data.update({
                "country":      req.location or lead_data.get("country"),
                "state":        req.state or lead_data.get("state"),
                "city":         req.city or lead_data.get("city"),
                "company_size": req.company_size or lead_data.get("company_size"),
            })
            save_or_update_lead(db, lead_data)
            
    return result


@router.post("/api/ai-search")
async def ai_search(req: AISearchRequest, db: Session = Depends(get_db)):
    prompt = req.prompt.lower()

    job_titles: list[str] = []
    if "founder"   in prompt: job_titles.append("Founder")
    if "ceo"       in prompt: job_titles.append("CEO")
    if "cto"       in prompt: job_titles.append("CTO")
    if "marketing" in prompt: job_titles.append("Marketing Manager")
    if "product"   in prompt: job_titles.append("Product Manager")

    industry = ""
    if "ai" in prompt or "artificial intelligence" in prompt: industry = "Artificial Intelligence"
    elif "fintech"    in prompt: industry = "FinTech"
    elif "healthcare" in prompt: industry = "Healthcare"
    elif "saas"       in prompt: industry = "SaaS"
    elif "e-commerce" in prompt or "ecommerce" in prompt: industry = "E-Commerce"

    size_match = re.search(r"(\d+)[^\d]*(\d+)", prompt)
    min_s, max_s = (int(size_match.group(1)), int(size_match.group(2))) if size_match else (1, 200)

    filters = {
        "job_titles":       job_titles or ["Founder", "CEO"],
        "industry":         industry,
        "company_size_min": min_s,
        "company_size_max": max_s,
        "page":             1,
    }

    result = await fetch_apollo_leads(filters)
    
    # Automate database push for all extracted leads
    if "leads" in result:
        for lead_data in result["leads"]:
            # Merge parsed AI filters
            lead_data.update({
                "country":      lead_data.get("country"), # AI might not parse country yet
                "industry":     filters.get("industry") or lead_data.get("industry"),
                "company_size": f"{filters['company_size_min']}-{filters['company_size_max']}" if not lead_data.get("company_size") else lead_data.get("company_size"),
            })
            save_or_update_lead(db, lead_data)

    return {**result, "filters_used": filters}
