__tags__ = ["users"]
__prefix__ = "/users"

from fastapi import APIRouter, HTTPException, status

from wrap.applications.user import UserCRUD, User
from wrap.applications.user.dependencies import CurrentUser
from wrap.core.utils.crypto import email_hotp
from wrap.core.utils.transporter import send_confirm_email

router = APIRouter()


@router.get("/", response_model=User)
async def get_by(email: str = "") -> User | list[User] | None:
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
    if email:
        if not (user := await UserCRUD.get_by(email=email)):
            raise not_found

        return await User.from_tortoise_orm(user)


@router.post("/sendConfirmationEmail")
async def send_confirmation_email(
        email: str,
        current_user: CurrentUser
):
    if current_user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email Already Confirmed"
        )

    if current_user.email != email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown Email"
        )

    return send_confirm_email(email, current_user.id)


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
