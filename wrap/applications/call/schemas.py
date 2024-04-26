from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import CallORM
from wrap.core.bases import ISOString

Call = pydantic_model_creator(CallORM)


class CallPayload(BaseModel):
    therapist_id: int
    event_id: int
    participants: list[int]
    datetime: ISOString
