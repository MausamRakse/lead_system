import logging
import httpx
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

CSC_BASE = "https://api.countrystatecity.in/v1"

_cached_countries: list[dict] = []
_cached_states: dict[str, list[dict]] = {}
_cached_cities: dict[str, list[dict]] = {}


async def get_countries() -> list[dict]:
    global _cached_countries
    if _cached_countries:
        return _cached_countries

    api_key = settings.CSC_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="CSC_API_KEY not configured.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CSC_BASE}/countries", headers={"X-CSCAPI-KEY": api_key}, timeout=10.0)
            response.raise_for_status()
            countries = [{"name": c.get("name"), "iso2": c.get("iso2")} for c in response.json()]
            countries.sort(key=lambda x: x["name"])
            _cached_countries = countries
            return countries
        except Exception as e:
            logger.error("Failed to fetch countries: %s", e)
            raise HTTPException(status_code=500, detail=f"Failed to fetch countries: {str(e)}")


async def get_states(iso2: str) -> list[dict]:
    global _cached_states
    iso2 = iso2.upper()
    if iso2 in _cached_states:
        return _cached_states[iso2]

    api_key = settings.CSC_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="CSC_API_KEY not configured.")

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{CSC_BASE}/countries/{iso2}/states", headers={"X-CSCAPI-KEY": api_key}, timeout=10.0)
            if res.status_code == 404:
                return []
            res.raise_for_status()
            states = [{"name": s.get("name"), "iso2": s.get("iso2")} for s in res.json()]
            states.sort(key=lambda x: x["name"])
            _cached_states[iso2] = states
            return states
        except Exception as e:
            logger.error("Failed to fetch states for %s: %s", iso2, e)
            raise HTTPException(status_code=500, detail=f"Failed to fetch states: {str(e)}")


async def get_cities(ciso: str, siso: str) -> list[dict]:
    global _cached_cities
    ciso = ciso.upper()
    siso = siso.upper()
    cache_key = f"{ciso}-{siso}"

    if cache_key in _cached_cities:
        return _cached_cities[cache_key]

    api_key = settings.CSC_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="CSC_API_KEY not configured.")

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"{CSC_BASE}/countries/{ciso}/states/{siso}/cities",
                headers={"X-CSCAPI-KEY": api_key},
                timeout=15.0,
            )
            if res.status_code == 404:
                return []
            res.raise_for_status()
            cities = [{"name": c.get("name")} for c in res.json()]
            cities.sort(key=lambda x: x["name"])
            _cached_cities[cache_key] = cities
            return cities
        except Exception as e:
            logger.error("Failed to fetch cities for %s/%s: %s", ciso, siso, e)
            raise HTTPException(status_code=500, detail=f"Failed to fetch cities: {str(e)}")
