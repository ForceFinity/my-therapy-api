__tags__ = ["users"]
__prefix__ = "/users"

from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Form
from starlette.responses import JSONResponse
from tortoise.expressions import Q

from wrap.applications.user import UserCRUD, User
from wrap.applications.user.dependencies import CurrentUser, CurrentConfirmed, CurrentAdmin
from wrap.applications.user.models import UserType
from wrap.core.utils.crypto import email_hotp
from wrap.core.utils.transporter import send_confirm_email

router = APIRouter()


@router.get("/")
async def get_by(
        id: int = None,
        email: str = None,
        is_therapist: bool = None,
        offset: int = None,
        limit: int = None
) -> User | list[User] | None:
    limit = limit if limit and (limit <= 50) else 50
    query = UserCRUD.model.all()

    if id:
        return await query.get_or_none(id=id)

    if offset:
        query = query.offset(offset)

    if email:
        query = query.filter(email=email)

    if is_therapist is not None:
        query = query.filter(
            Q(account_type=UserType.THERAPIST)
            if is_therapist
            else ~Q(account_type=UserType.THERAPIST)
        )

    return await query.order_by("id").limit(limit)


@router.post("/pfp")
async def set_pfp(
        pfp_url: Annotated[str, Form()],
        current_confirmed: CurrentConfirmed
):
    return await UserCRUD.set_pfp(current_confirmed.id, pfp_url)


@router.get("/pfp")
async def get_pfp(current_user: CurrentConfirmed):
    return await UserCRUD.get_pfp(current_user.id)
