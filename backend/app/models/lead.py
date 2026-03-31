from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(255))
    title        = Column(String(255))
    company_name = Column(String(255))
    about_company = Column(Text)
    email        = Column(String(255), unique=True, index=True)
    phone        = Column(String(50))
    linkedin_url = Column(Text)
    industry     = Column(String(255))
    country      = Column(String(255))
    state        = Column(String(255))
    city         = Column(String(255))
    company_size = Column(String(50))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
