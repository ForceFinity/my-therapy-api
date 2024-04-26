__tags__ = ["users", "oauth2"]
__prefix__ = "/oauth2"

from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm

from wrap.applications.user import Token, UserCRUD, RefereedCRUD
from wrap.applications.user.schemas import TokenDecoded, UserPayload, UserResponse, User, RefereedPayload
from wrap.core.utils import crypt

router = APIRouter()


@router.post("/", response_model=Token)
async def auth_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await UserCRUD.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect nickname or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=crypt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crypt.create_jwt_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )

    return Token(accessToken=access_token, token_type="Bearer")


@router.get("/verify/", response_model=TokenDecoded)
async def verify_token(token: Annotated[str, Depends(crypt.oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not (decoded := crypt.decode_auth_jwt(token)):
        raise credentials_exception

    if not await UserCRUD.get_by(email=decoded.email):
        raise credentials_exception

    return decoded


@router.post("/sign-up/", response_model=UserResponse)
async def sign_up(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        nickname: Annotated[str, Form()],
        birth_date: Annotated[str, Form()],
        by_user_id: str = "",
        is_by_google: bool = False
):
    if await UserCRUD.get_by(email=form_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    access_token_expires = timedelta(minutes=crypt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crypt.create_jwt_token(
        data={"email": form_data.username}, expires_delta=access_token_expires
    )

    user = await UserCRUD.create_by(
        UserPayload(
            nickname=nickname,
            birth_date=datetime.fromisoformat(birth_date).date(),
            email=form_data.username,
            password=form_data.password,
            is_confirmed=is_by_google
        )
    )

    if by_user_id:
        await RefereedCRUD.create_by(RefereedPayload(user_id=by_user_id, refereed_id=str(user.id)))

    resp = UserResponse(
        **(await User.from_tortoise_orm(user)).model_dump(),
        access_token=access_token,
        token_type="Bearer"
    )

    return resp.copy(exclude={"password_hash"})
