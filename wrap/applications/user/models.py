from tortoise import fields

from wrap.core.bases import BaseModel


class UserORM(BaseModel):
    nickname = fields.CharField(max_length=64)
    email = fields.CharField(max_length=256, unique=True)
    birth_date = fields.DateField()
    password_hash = fields.CharField(max_length=512)
    is_confirmed = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_questionnaire_complete = fields.BooleanField(default=False)

    refereed: fields.ReverseRelation["UserORM"]
    users: fields.ReverseRelation["UserORM"]

    class Meta:
        table = "users"


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
