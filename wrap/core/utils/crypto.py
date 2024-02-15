import os
from datetime import datetime, timezone, timedelta

import pyotp
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from wrap.applications.user import TokenDecoded

SECRET_KEY = os.environ["SECRET_KEY"]
EMAIL_SECRET_KEY = os.environ["EMAIL_SECRET_KEY"]
ALGORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 28 * 24 * 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/oauth2/")

email_hotp = pyotp.HOTP(os.environ["EMAIL_HOTP_SECRET"])
phone_hotp = pyotp.HOTP(os.environ["PHONE_HOTP_SECRET"])


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    secret_key: str = SECRET_KEY
):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

    return encoded_jwt


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def decode_auth_jwt(token: str) -> TokenDecoded | None:
    try:
        return TokenDecoded(
            **jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        )
    except JWTError:
        return None
