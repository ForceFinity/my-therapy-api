from typing import Annotated

from fastapi import Depends, HTTPException, status

from .crud import UserCRUD
from .schemas import User
from .models import UserType
from wrap.core.utils import crypto


async def get_current_user(token: Annotated[str, Depends(crypto.oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not (decoded := crypto.decode_auth_jwt(token)):
        raise credentials_exception

    if not (user := await UserCRUD.get_by(email=decoded.email)):
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_admin(user: CurrentUser) -> User:
    if user.account_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )

    return user


async def get_current_confirmed(user: CurrentUser) -> User:
    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed"
        )

    return user


async def get_current_therapist(user: CurrentUser) -> User:
    if user.account_type != UserType.THERAPIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not therapist"
        )

    return user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]
CurrentConfirmed = Annotated[User, Depends(get_current_confirmed)]
CurrentTherapist = Annotated[User, Depends(get_current_therapist)]
