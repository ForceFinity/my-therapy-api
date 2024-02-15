from typing import Union

from tortoise import Model, fields
from pydantic import BaseModel as PydanticModel
from tortoise.exceptions import DoesNotExist

from wrap.core import logger


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseCRUD:
    model: BaseModel

    @classmethod
    async def create_by(cls, payload: PydanticModel) -> "model":
        instance = await cls.model.create(**payload.model_dump())

        logger.debug(f"New {str(instance)} id={instance.id} was created.")

        return instance

    @classmethod
    async def get_by(cls, **kwargs) -> Union["model", None]:
        logger.debug(f"Getting `{cls.model.__name__}` by {kwargs}")

        return await cls.model.get_or_none(**kwargs)

    @classmethod
    async def get_all(cls) -> list["model"]:
        logger.debug(f"Getting all `{cls.model.__name__}` records")

        return await cls.model.all()

    @classmethod
    async def filter_by(cls, **kwargs) -> list["model"]:
        logger.debug(f"Filtering {cls.model.__name__} instances by {kwargs}")
        try:
            return await cls.model.filter(**kwargs)

        except DoesNotExist as e:
            logger.error(e)
            raise e

    @classmethod
    async def update_by(cls, payload: PydanticModel | dict, **kwargs) -> "model":
        instance = await cls.get_by(**kwargs)
        as_dict = payload.items() if isinstance(payload, dict) else payload.model_dump().items()

        await instance.update_from_dict(
            {
                key: value for key, value in as_dict
                if value is not None
            }
        ).save()
        logger.debug(f"{str(instance)} id={instance.id} was updated.")

        return instance

    @classmethod
    async def delete_by(cls, **kwargs) -> None:
        instance = await cls.get_by(**kwargs)

        logger.debug(f"Deleting {str(instance)} id={instance.id}")

        await instance.delete()
