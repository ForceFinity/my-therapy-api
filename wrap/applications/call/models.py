from tortoise import fields
from tortoise.contrib.postgres import fields as p_fields

from wrap.applications.user.models import UserORM
from wrap.core.bases import BaseModel


class CallORM(BaseModel):
    id = fields.CharField(max_length=256, unique=True, pk=True)
    therapist: fields.ForeignKeyRelation[UserORM] = fields.ForeignKeyField(
        "models.UserORM", related_name="calls"
    )
    participants = p_fields.ArrayField("int")
    datetime = fields.DatetimeField()

    class Meta:
        table = "calls"
