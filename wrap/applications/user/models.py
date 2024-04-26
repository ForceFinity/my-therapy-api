from enum import IntEnum
from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.contrib.postgres.fields import ArrayField

from wrap.core.bases import BaseModel

if TYPE_CHECKING:
    from wrap.applications.call.models import CallORM


class UserType(IntEnum):
    CLIENT = 1
    THERAPIST = 2
    ADMIN = 3


class EventType(IntEnum):
    SESSION = 1
    SUPERVISION = 2
    OTHER = 3


class UserORM(BaseModel):
    nickname = fields.CharField(max_length=64)
    email = fields.CharField(max_length=256, unique=True)
    birth_date = fields.DateField()
    password_hash = fields.CharField(max_length=512)
    account_type = fields.IntEnumField(UserType, default=UserType.CLIENT)
    is_confirmed = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_questionnaire_complete = fields.BooleanField(default=False)

    pfp_url: fields.ReverseRelation["UserPFPORM"]
    therapist_data: fields.ReverseRelation["TherapistDataORM"]
    therapist_info: fields.ReverseRelation["TherapistInfoORM"]
    events: fields.ReverseRelation["TherapistEventORM"]

    class Meta:
        table = "users"


class UserPFPORM(BaseModel):
    pfp_url = fields.CharField(max_length=512, null=True)
    user: fields.OneToOneRelation["UserORM"] = fields.OneToOneField(
        "models.UserORM", "pfp_url"
    )

    class Meta:
        table = "user_pfp"


class TherapistDataORM(BaseModel):
    therapist: fields.ForeignKeyRelation[UserORM] = fields.ForeignKeyField(
        "models.UserORM", related_name="therapist_data"
    )

    events: fields.ReverseRelation["TherapistEventORM"]
    notes: fields.ReverseRelation["TherapistNoteORM"]

    class Meta:
        table = "therapist_data"


class TherapistEventORM(BaseModel):
    therapist_data: fields.ForeignKeyRelation[TherapistDataORM] = fields.ForeignKeyField(
        "models.TherapistDataORM", related_name="events"
    )
    client: fields.ForeignKeyRelation[UserORM] = fields.ForeignKeyField(
        "models.UserORM", related_name="events", null=True
    )

    title = fields.CharField(32)
    description = fields.CharField(1024)
    event_datetime = fields.DatetimeField()
    type = fields.IntEnumField(EventType, default=EventType.SESSION)

    class Meta:
        table = "therapist_events"


class TherapistNoteORM(BaseModel):
    therapist_data: fields.ForeignKeyRelation[TherapistDataORM] = fields.ForeignKeyField(
        "models.TherapistDataORM", related_name="notes"
    )
    client: fields.ForeignKeyRelation[UserORM] = fields.ForeignKeyField(
        "models.UserORM", related_name="notes", null=True
    )
    content = fields.CharField(1024)

    class Meta:
        table = "therapist_notes"


class TherapistInfoORM(BaseModel):
    therapist: fields.ForeignKeyRelation[UserORM] = fields.ForeignKeyField(
        "models.UserORM", related_name="therapist_info"
    )
    price = fields.IntField()
    about = fields.CharField(1024)
    education = ArrayField("text")
    theme_ids = ArrayField("int")
    work_hours = ArrayField("timestamptz")

    class Meta:
        table = "therapist_info"


class RefereedORM(BaseModel):
    is_questionnaire_complete = fields.BooleanField(default=False)
    user: fields.ForeignKeyRelation["UserORM"] = fields.ForeignKeyField(
        "models.UserORM", related_name="users"
    )
    refereed: fields.ForeignKeyRelation["UserORM"] = fields.ForeignKeyField(
        "models.UserORM", related_name="refereed"
    )

    class Meta:
        table = "by_user_to_refereed"
