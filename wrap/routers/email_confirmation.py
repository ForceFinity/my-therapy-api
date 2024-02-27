__tags__ = ["users", "email_confirmation"]
__prefix__ = "/users"

from fastapi import APIRouter, HTTPException, status, Form

from wrap.applications.user import User, UserCRUD
from wrap.applications.user.dependencies import CurrentUser
from wrap.core.utils import transporter
from wrap.core.utils.crypto import email_hotp

router = APIRouter()


@router.post("/sendConfirmationEmail")
async def send_confirmation_email(current_user: CurrentUser):
    if current_user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email Already Confirmed"
        )

    return await transporter.send_confirm_email(current_user.email, current_user.id)


@router.post("/confirm")
async def confirm_email(
        otp: str,
        current_user: CurrentUser
) -> User:
    if current_user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email Already Confirmed"
        )

    if not email_hotp.verify(otp, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code"
        )

    user = await UserCRUD.update_by({"is_confirmed": True}, id=current_user.id)

    return User.from_orm(user)
