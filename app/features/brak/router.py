from fastapi import APIRouter

router = APIRouter(
    prefix="/brak"
)


@router.get("/")
async def root():
    return ""


@router.get("/brak/user/{user_id}")
async def say_hello(user_id: int):
    return "get_brak_by_user_id(user_id)"


@router.get("/brak/kid/{kid_id}")
async def say_hello(kid_id: int):
    return "get_brak_by_kid_id(kid_id)"
