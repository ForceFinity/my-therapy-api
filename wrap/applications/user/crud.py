from fastapi import HTTPException, status

from .models import UserORM, RefereedORM, UserPFPORM
from .schemas import UserPayload, UserSchema, Refereed
from wrap.core.utils import crypto
from wrap.core.bases import BaseCRUD


class UserCRUD(BaseCRUD):
    model = UserORM

    @classmethod
    async def create_by(cls, payload: UserPayload) -> model:
        password_hash = crypto.get_password_hash(payload.password)

        hashed_payload = UserSchema(
            **payload.copy(exclude={"password"}).model_dump(),
            password_hash=password_hash
        )

        return await super().create_by(hashed_payload)

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> model | bool:
        user = await cls.get_by(email=email)

        if not user:
            return False

        if not crypto.verify_password(password, user.password_hash):
            return False

        return user

    @classmethod
    async def set_pfp(cls, user_id: int, pfp_url: str) -> UserPFPORM:
        if user_pfp := await UserPFPORM.get_or_none(user_id=user_id):
            await user_pfp.update_from_dict({"pfp_url": pfp_url})
            await user_pfp.save()
        else:
            user_pfp = await UserPFPORM.create(user_id=user_id, pfp_url=pfp_url)

        return user_pfp

    @classmethod
    async def get_pfp(cls, user_id: int) -> str:
        if not (pfp := await UserPFPORM.get_or_none(user_id=user_id)):
            return ""

        return pfp.pfp_url


class RefereedCRUD(BaseCRUD):
    model = RefereedORM
