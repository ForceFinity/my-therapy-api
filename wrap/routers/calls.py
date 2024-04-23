__tags__ = ["calls"]
__prefix__ = "/calls"

import os
from datetime import timedelta, datetime as dt
from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, status, Form

from wrap.applications.call import CallCRUD, Call, CallPayload
from wrap.applications.user.dependencies import CurrentConfirmed
from wrap.core.utils import crypt

router = APIRouter()


@router.get("/")
async def get_calls(therapist_id=Query(None), client_id=Query(None)) -> list[Call]:
    if all([therapist_id, client_id]):
        return await CallCRUD.filter_by(therapist_id=therapist_id, client_id=client_id)
    elif therapist_id:
        return await CallCRUD.filter_by(therapist_id=therapist_id)
    elif client_id:
        return await CallCRUD.filter_by(client_id=client_id)
    else:
        return await CallCRUD.get_all()


@router.post("/")
async def plan_call(
    current_confirmed: CurrentConfirmed,
    therapist_id: Annotated[int, Form()],
    participants: Annotated[str, Form()],
    datetime: Annotated[str, Form()]
) -> Call:
    return await CallCRUD.create_by(
        CallPayload(
            therapist_id=therapist_id,
            participants=participants.split(";"),
            datetime=datetime
        )
    )


@router.get("/token")
async def get_user_call_token(current_confirmed: CurrentConfirmed):
    access_token_expires = timedelta(minutes=crypt.USER_CALL_TOKEN_EXPIRE_MINUTES)

    return crypt.create_jwt_token(
        data={"user_id": current_confirmed.email},
        expires_delta=access_token_expires,
        secret_key=os.environ["GETSTREAM_SECRET_KEY"],
        algorithm=crypt.Algorithms.HS256
    )
