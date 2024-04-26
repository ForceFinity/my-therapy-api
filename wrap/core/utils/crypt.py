import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum

import pyotp
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from wrap.applications.user import TokenDecoded


@dataclass
class Algorithms:
    HS512 = "HS512"
    HS256 = "HS256"


SECRET_KEY = os.environ["SECRET_KEY"]
EMAIL_SECRET_KEY = os.environ["EMAIL_SECRET_KEY"]
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 28
USER_CALL_TOKEN_EXPIRE_MINUTES = 60 * 24 * 28

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/oauth2/")

email_hotp = pyotp.HOTP(os.environ["EMAIL_HOTP_SECRET"])
phone_hotp = pyotp.HOTP(os.environ["PHONE_HOTP_SECRET"])


def get_bcrypt_hash(secret):
    return pwd_context.hash(secret)


def create_jwt_token(
    data: dict,
    expires_delta: timedelta | None = None,
    secret_key: str = SECRET_KEY,
    algorithm: str = Algorithms.HS512
):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt


def verify_secret(secret, hashed_secret):
    return pwd_context.verify(secret, hashed_secret)


def decode_auth_jwt(token: str) -> TokenDecoded | None:
    try:
        return TokenDecoded(
            **jwt.decode(token, SECRET_KEY, algorithms=[Algorithms.HS512])
        )
    except JWTError:
        return None
