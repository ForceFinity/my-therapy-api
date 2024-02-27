import datetime
from typing import ClassVar

from pydantic import BaseModel, Field, AliasChoices
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import UserORM, RefereedORM, UserType

Refereed = pydantic_model_creator(RefereedORM)


class RefereedPayload(BaseModel):
    refereed_id: str
    user_id: str


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


class Token(BaseModel):
    access_token: str = Field(
        validation_alias=AliasChoices("accessToken", "access_token")
    )


class UserResponse(User, Token):
    pass


class TokenDecoded(BaseModel):
    email: str | None
    exp: int | None


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
