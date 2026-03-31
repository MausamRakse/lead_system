import logging
import httpx
from fastapi import HTTPException
from app.config import settings
from utils.extractors import extract_email, extract_phone

logger = logging.getLogger(__name__)

APOLLO_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
APOLLO_ENRICH_URL = "https://api.apollo.io/api/v1/people/match"


async def enrich_person(client: httpx.AsyncClient, api_key: str, person_id: str) -> dict:
    """Enrich a single Apollo person by ID."""
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type":  "application/json",
        "accept":        "application/json",
        "X-Api-Key":     api_key,
    }
    payload = {
        "id":                     person_id,
        "reveal_personal_emails": True,
        "reveal_phone_number":    False,
        "webhook_url":            settings.WEBHOOK_URL,
    }
    try:
        response = await client.post(APOLLO_ENRICH_URL, headers=headers, json=payload, timeout=15.0)
        logger.info("Enrich status for %s: %s", person_id, response.status_code)
        if response.status_code == 200:
            person = response.json().get("person", {}) or {}
            logger.info("Enrich email: %s", extract_email(person))
            return person
    except Exception as e:
        logger.error("Enrich error for %s: %s", person_id, e)
    return {}


async def fetch_apollo_leads(filters: dict) -> dict:
    """Search Apollo for leads matching the given filters, enrich, and return results."""
    api_key = settings.APOLLO_API_KEY
    headers = {
        "X-Api-Key":    api_key,
        "Content-Type": "application/json",
    }

    payload: dict = {
        "page":     filters.get("page", 1),
        "per_page": min(filters.get("total_leads", 10), 100),
    }

    if filters.get("job_title"):
        payload["person_titles"] = [filters["job_title"]]
    elif filters.get("job_titles"):
        payload["person_titles"] = filters["job_titles"]

    loc_parts: list[str] = []
    if filters.get("city"):
        loc_parts.append(filters["city"])
    if filters.get("state"):
        loc_parts.append(filters["state"])
    if filters.get("location"):
        loc_parts.append(filters["location"])
    if loc_parts:
        payload["person_locations"] = [", ".join(loc_parts)]

    company_size = filters.get("company_size")
    if company_size:
        parts = company_size.split("-")
        if len(parts) == 2:
            payload["organization_num_employees_ranges"] = [f"{parts[0]},{parts[1]}"]
        elif "+" in company_size:
            payload["organization_num_employees_ranges"] = [f"{company_size.replace('+', '')},1000000"]
    elif "company_size_min" in filters and "company_size_max" in filters:
        payload["organization_num_employees_ranges"] = [
            f"{filters['company_size_min']},{filters['company_size_max']}"
        ]

    tags: list[str] = []
    if filters.get("industry"):
        tags.append(filters["industry"])
    if filters.get("keywords"):
        tags.extend([k.strip() for k in filters["keywords"].split(",") if k.strip()])
    if tags:
        payload["q_organization_keyword_tags"] = tags

    logger.info("Apollo search payload: %s", payload)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(APOLLO_SEARCH_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            raw_people = data.get("people", [])
            requested_limit = int(filters.get("total_leads") or 10)
            people = raw_people[: min(requested_limit, len(raw_people))]

            leads: list[dict] = []
            for p in people:
                enriched = await enrich_person(client, api_key, p.get("id", ""))
                merged = {**p, **enriched}
                org = merged.get("organization", {}) or {}

                raw_desc = (
                    org.get("short_description")
                    or org.get("seo_description")
                    or org.get("description")
                    or "No company info available"
                )
                about = (raw_desc[:100] + "...") if len(raw_desc) > 100 else raw_desc

                leads.append({
                    "id":            p.get("id", ""),
                    "name":          f"{merged.get('first_name', '')} {merged.get('last_name', '')}".strip() or "Unknown",
                    "title":         merged.get("title", "Unknown Title"),
                    "company":       org.get("name", "Unknown Company"),
                    "email":         extract_email(merged),
                    "phone":         extract_phone(merged),
                    "linkedin_url":  merged.get("linkedin_url", ""),
                    "about_company": about,
                    "country":       merged.get("country") or org.get("country") or "",
                    "state":         merged.get("state") or org.get("state") or "",
                    "city":          merged.get("city") or org.get("city") or "",
                    "company_size":  str(org.get("estimated_num_employees") or org.get("employee_count") or ""),
                    "industry":      org.get("industry") or merged.get("industry") or filters.get("industry") or "",
                })

            filtered_leads = [
                lead for lead in leads
                if lead.get("email") not in ["", None, "Not available"]
                and lead.get("phone") not in ["", None, "Not available"]
            ]

            valid_count = len(filtered_leads)
            raw_processed_count = len(people)
            removed_count = raw_processed_count - valid_count

            if raw_processed_count == 0:
                message = "No data provided by backend"
            elif valid_count == 0:
                message = "No valid leads found"
            elif valid_count < requested_limit:
                message = f"We found only {valid_count} valid leads"
            else:
                message = f"Successfully found {requested_limit} leads"

            return {
                "leads":        filtered_leads,
                "count":        valid_count,
                "raw_processed": raw_processed_count,
                "removed_count": removed_count,
                "message":      message,
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Apollo API error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
