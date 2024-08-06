from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict

from app.database.mongo import users
from app.models.PyObjectId import PyObjectId


class User(BaseModel):
    OId: PyObjectId = Field(..., alias="_id")
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: str
    is_admin: Optional[bool] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "0",
                "id": 0,
                "first_name": "first_name",
                "last_name": "last_name",
                "username": "username",
                "language_code": "ru",
            }
        },
    )

    @classmethod
    def from_mongo(cls, data: dict):
        if data is None:
            return None
        return cls(**data)


def get_user_by_id(user_id: int) -> User | None:
    user_data = users.find_one({"id": user_id})
    if user_data is None:
        return None
    return User.from_mongo(user_data)
