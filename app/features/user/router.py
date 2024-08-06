from fastapi import APIRouter, HTTPException

from app.database.mongo import users
from app.features.user.model import User, get_user_by_id

router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@router.get("/", responses={404: {"description": "User not found"}})
async def random_user() -> User:
    data = users.find_one()
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_mongo(data)


@router.get("/{user_id}", responses={404: {"description": "User with user_id={user_id} not found"}})
async def user_by_id(user_id: int) -> User:
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return user

