from fastapi import APIRouter, HTTPException

from app.database.mongo import braks
from app.features.brak.model import get_brak_by_user_id, get_brak_by_kid_id, Brak

router = APIRouter(
    prefix="/brak",
    tags=["braks"]
)


@router.get("/", responses={404: {"description": "Brak not found"}})
async def random_brak() -> Brak:
    data = braks.find_one()
    if data is None:
        raise HTTPException(status_code=404, detail=f"Brak not found")
    return Brak.from_mongo(data)


@router.get("/user/{user_id}", responses={404: {"description": "Brak with user_id={user_id} not found"}})
async def brak_by_user_id(user_id: int) -> Brak:
    brak = get_brak_by_user_id(user_id)
    if brak is None:
        raise HTTPException(status_code=404, detail=f"Brak with user_id={user_id} not found")
    return brak


@router.get("/kid/{kid_id}", responses={404: {"description": "Brak with kid_id={kid_id} not found"}})
async def brak_by_kid_id(kid_id: int) -> Brak:
    brak = get_brak_by_kid_id(kid_id)
    if brak is None:
        raise HTTPException(status_code=404, detail=f"Brak with kid_id={kid_id} not found")
    return brak
