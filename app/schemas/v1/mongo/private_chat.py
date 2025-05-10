from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.v1.mongo.common import PyObjectId, MongoBaseModel
from bson import ObjectId

class PrivateChatCreate(MongoBaseModel):
    user1_id: int
    user2_id: int
    last_message: Optional[dict] = None


class PrivateChatInDB(MongoBaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user1_id: int
    user2_id: int
    last_message: Optional[dict] = None

    @classmethod
    def from_mongo(cls, data: dict):
        # Преобразуем ObjectId в строку
        data["_id"] = str(data["_id"])
        return cls(**data)
    class Config:
        orm_mode = True  # Это важно для конвертации данных в модели Pydantic