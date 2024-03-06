from wrap.core.bases import BaseCRUD
from wrap.core.utils import crypto
from .models import UserORM, RefereedORM, UserPFPORM, TherapistDataORM, TherapistEventORM, TherapistNoteORM, \
    TherapistInfoORM, EventType
from .schemas import UserPayload, UserSchema, EventPayload


class UserCRUD(BaseCRUD[UserORM]):
    model = UserORM

    @classmethod
    async def create_by(cls, payload: UserPayload):
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


class TherapistDataCRUD(BaseCRUD[TherapistDataORM]):
    model = TherapistDataORM

    @classmethod
    async def get_therapist_data(cls, id_: int) -> TherapistDataORM:
        if not (therapist_data := await cls.get_by(therapist_id=id_)):
            therapist_data = await cls.model.create(therapist_id=id_)

        return therapist_data

    @classmethod
    async def get_events(cls, id_: int) -> list[TherapistEventORM]:
        therapist_data = await cls.get_therapist_data(id_)

        return await therapist_data.events.order_by("event_datetime")

    @classmethod
    async def add_event(cls, id_: int, event: EventPayload) -> TherapistEventORM:
        therapist_data = await cls.get_therapist_data(id_)

        return await TherapistEventORM.create(**event.model_dump(), therapist_data_id=therapist_data.id)

    @classmethod
    async def get_sessions(cls, id_: int):
        therapist_data = await cls.get_therapist_data(id_)

        return await TherapistEventORM.filter(
            therapist_data_id=therapist_data.id, type=EventType.SESSION
        ).all()

    @classmethod
    async def get_note(cls, id_: int, client_id: int) -> TherapistNoteORM | None:
        therapist_data = await cls.get_therapist_data(id_)

        return await TherapistNoteORM.get_or_none(therapist_data_id=therapist_data.id, client_id=client_id)

    @classmethod
    async def add_note(cls, id_: int, client_id: int, content: str):
        therapist_data = await cls.get_therapist_data(id_)

        return await TherapistNoteORM.create(
            therapist_data_id=therapist_data.id,
            client_id=client_id,
            content=content
        )


class TherapistInfoCRUD(BaseCRUD[TherapistInfoORM]):
    model = TherapistInfoORM


class RefereedCRUD(BaseCRUD):
    model = RefereedORM
