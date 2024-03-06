import datetime
from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field, AliasChoices
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import UserORM, RefereedORM, UserType, TherapistEventORM, TherapistDataORM, TherapistNoteORM, \
    TherapistInfoORM

Refereed = pydantic_model_creator(RefereedORM)
Event = pydantic_model_creator(TherapistEventORM)
Note = pydantic_model_creator(TherapistNoteORM)
TherapistInfoPayload = pydantic_model_creator(TherapistInfoORM, include=("about", "education", "price"))


class TherapistInfo(pydantic_model_creator(TherapistInfoORM)):
    therapist_id: int
    work_hours: list[datetime.datetime]


class TherapistInfoFull(TherapistInfo):
    pfp: str
    name: str


class RefereedPayload(BaseModel):
    refereed_id: str
    user_id: str


class Token(BaseModel):
    access_token: str = Field(
        validation_alias=AliasChoices("accessToken", "access_token")
    )
    token_type: str


class TokenDecoded(BaseModel):
    email: str | None
    exp: int | None


class User(pydantic_model_creator(UserORM)):
    is_confirmed: bool = Field(
        validation_alias=AliasChoices("isConfirmed", "is_confirmed"), default=False
    )
    is_active: bool = Field(
        validation_alias=AliasChoices("isActive", "is_active"), default=True
    )
    is_questionnaire_complete: bool = Field(
        validation_alias=AliasChoices("isQuestionnaireComplete", "is_questionnaire_complete"),
        default=False
    )
    password_hash: ClassVar[str]


class UserResponse(User, Token):
    pass


class EmailDecoded(BaseModel):
    email: str | None
    exp: int | None


class UserBase(BaseModel):
    nickname: str | None = None
    birth_date: datetime.date
    account_type: UserType = UserType.CLIENT
    email: str


class UserSchema(UserBase):
    password_hash: str


class UserPayload(UserBase):
    password: str


class EventPayload(pydantic_model_creator(TherapistEventORM, name="EventPayload", exclude=("created_at", "id"))):
    client_id: int


class EventResponse(pydantic_model_creator(TherapistEventORM, name="EventResponse")):
    client_id: int


TherapistData = pydantic_model_creator(TherapistDataORM, exclude=("created_at", "id"))
ISOString: TypeAlias = str
