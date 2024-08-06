import json
from datetime import datetime
from typing import Optional

from bson import json_util, ObjectId
from pydantic import BaseModel, Field, ConfigDict

from app.database.mongo import braks
from app.models.PyObjectId import PyObjectId


def parse_json(data):
    return json.loads(json_util.dumps(data))


class Brak(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    first_user_id: int
    second_user_id: int
    chat_id: Optional[int] = None
    create_date: datetime
    baby_user_id: Optional[int] = None
    baby_create_date: Optional[datetime] = None
    score: int
    last_casino_play: datetime
    last_grow_kid: datetime
    last_hamster_update: datetime
    tap_count: int
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "id": "0",
                "first_user_id": 0,
                "second_user_id": 0,
                "chat_id": 0,
                "create_date": "1970-01-01T00:00:00",
                "baby_user_id": 0,
                "baby_create_date": "1970-01-01T00:00:00",
                "score": 0,
                "last_casino_play": "1970-01-01T00:00:00",
                "last_grow_kid": "1970-01-01T00:00:00",
                "last_hamster_update": "1970-01-01T00:00:00",
                "tap_count": 0,
            }
        },
    )

    @classmethod
    def from_mongo(cls, data: dict):
        if data is None:
            return None
        return cls(**data)


def get_brak_by_id(brak_id: str) -> Brak | None:
    brak_data = braks.find_one({"_id": brak_id})
    if brak_data is None:
        return None
        # raise HTTPException(status_code=404, detail=f"Brak with brak_id= {brak_id} not found")
    return Brak.from_mongo(brak_data)


def get_brak_by_user_id(user_id: int) -> Brak | None:
    brak_data = braks.find_one({"$or": [{"first_user_id": user_id}, {"second_user_id": user_id}]})
    if brak_data is None:
        return None
    return Brak.from_mongo(brak_data)


def get_brak_by_kid_id(kid_id: int) -> Brak | None:
    brak_data = braks.find_one({"baby_user_id": kid_id})
    if brak_data is None:
        return None
    return Brak.from_mongo(brak_data)
