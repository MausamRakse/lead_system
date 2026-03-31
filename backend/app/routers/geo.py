from fastapi import APIRouter
from app.services.geo import get_countries, get_states, get_cities

router = APIRouter(tags=["geo"])


@router.get("/api/countries")
async def countries_endpoint():
    data = await get_countries()
    return {"countries": data}


@router.get("/api/countries/{iso2}/states")
async def states_endpoint(iso2: str):
    data = await get_states(iso2)
    return {"states": data}


@router.get("/api/countries/{ciso}/states/{siso}/cities")
async def cities_endpoint(ciso: str, siso: str):
    data = await get_cities(ciso, siso)
    return {"cities": data}
