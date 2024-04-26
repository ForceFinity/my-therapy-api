import base58

from .schemas import CallPayload
from wrap.applications.call.models import CallORM
from wrap.core import logger
from wrap.core.bases import BaseCRUD


class CallCRUD(BaseCRUD[CallORM]):
    model = CallORM

    @classmethod
    async def create_by(cls, payload: CallPayload) -> model:
        call_id = base58.b58encode(
            "".join({str(i) for i in payload.participants})
            + str(payload.therapist_id)
            + str(payload.datetime)
        ).lower().decode("utf-8")
        instance = await cls.model.create(**payload.model_dump(), id=call_id)

        logger.debug(f"New {str(instance)} id={instance.id} was created.")

        return instance
