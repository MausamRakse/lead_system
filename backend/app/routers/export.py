from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from utils.export import generate_csv_from_db

router = APIRouter(tags=["export"])


@router.get("/api/download-csv")
async def download_csv(db: Session = Depends(get_db)):
    return generate_csv_from_db(db)
