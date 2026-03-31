from typing import Optional
from pydantic import BaseModel, ConfigDict


class LeadRequest(BaseModel):
    industry:     Optional[str] = None
    location:     Optional[str] = None
    state:        Optional[str] = None
    job_title:    Optional[str] = None
    company_size: Optional[str] = None
    keywords:     Optional[str] = None
    city:         Optional[str] = None
    total_leads:  Optional[int] = 10
    page:         int = 1


class AISearchRequest(BaseModel):
    prompt: str


class EnrichRequest(BaseModel):
    person_id: str


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           Optional[int] = None
    name:         Optional[str] = None
    title:        Optional[str] = None
    company_name: Optional[str] = None
    about_company: Optional[str] = None
    email:        Optional[str] = None
    phone:        Optional[str] = None
    linkedin_url: Optional[str] = None
    industry:     Optional[str] = None
    country:      Optional[str] = None
    state:        Optional[str] = None
    city:         Optional[str] = None
    company_size: Optional[str] = None
