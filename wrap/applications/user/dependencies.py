from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from .crud import UserCRUD
from .schemas import User
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
