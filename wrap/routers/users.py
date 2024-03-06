__tags__ = ["users"]
__prefix__ = "/users"

import datetime
from typing import Annotated

from fastapi import APIRouter, Form, Query, HTTPException, status
from tortoise.expressions import Q

from wrap.applications.user import UserCRUD, User
from wrap.applications.user.crud import TherapistDataCRUD, TherapistInfoCRUD
from wrap.applications.user.dependencies import CurrentConfirmed, CurrentTherapist, CurrentUser
from wrap.applications.user.models import UserType, EventType, TherapistEventORM
from wrap.applications.user.schemas import EventPayload, Note, TherapistInfo, TherapistInfoPayload, TherapistInfoFull, \
    Event, EventResponse

router = APIRouter()


@router.get("/")
async def get_by(
        id_: Annotated[int, Query(alias="id")] = None,
        email: Annotated[str, Query()] = None,
        is_therapist: Annotated[bool, Query()] = None,
        offset: Annotated[int, Query()] = None,
        limit: Annotated[int, Query()] = None
) -> User | list[User] | None:
    limit = limit if limit and (limit <= 50) else 50
    query = UserCRUD.model.all()

    if id_:
        return await query.get_or_none(id=id_)

    if offset:
        query = query.offset(offset)

    if email:
        return await query.get_or_none(email=email)

    if is_therapist is not None:
        query = query.filter(
            Q(account_type=UserType.THERAPIST)
            if is_therapist
            else ~Q(account_type=UserType.THERAPIST)
        )

    return await query.filter(is_active=True).order_by("id").limit(limit)


@router.post("/pfp")
async def set_pfp(
        pfp_url: Annotated[str, Form()],
        current_confirmed: CurrentConfirmed
):
    return await UserCRUD.set_pfp(current_confirmed.id, pfp_url)


@router.get("/pfp")
async def get_pfp(current_confirmed: CurrentConfirmed):
    return await UserCRUD.get_pfp(current_confirmed.id)


@router.get("/therapistData/events", response_model=list[EventResponse])
async def get_events(
        current_therapist: CurrentTherapist,
        type_: Annotated[EventType, Query(alias="type")] = None
):
    if type_:
        return await TherapistEventORM.filter(
            therapist_data_id=(await TherapistDataCRUD.get_therapist_data(current_therapist.id)).id,
            type=type_
        ).order_by("event_datetime")

    return await TherapistDataCRUD.get_events(current_therapist.id)


@router.post("/therapistData/events", description="event_datetime field must be specified in ISO standard")
async def add_event(
        current_therapist: CurrentConfirmed,
        therapist_id: Annotated[int, Query()],
        client_id: Annotated[int, Form()],
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        event_datetime: Annotated[datetime.datetime, Form()]
) -> EventResponse:
    payload = EventPayload(
        client_id=client_id,
        title=title,
        description=description,
        event_datetime=event_datetime,
    )
    return await EventResponse.from_tortoise_orm(await TherapistDataCRUD.add_event(therapist_id, payload))


@router.get("/therapistData/notes")
async def get_note(
        current_therapist: CurrentTherapist,
        client_id: Annotated[int, Query()]
) -> Note | None:
    return await TherapistDataCRUD.get_note(current_therapist.id, client_id)


@router.post("/therapistData/notes")
async def get_note(
        current_therapist: CurrentTherapist,
        client_id: Annotated[int, Query()],
        content: Annotated[str, Form(max_length=1024)]
) -> Note | None:
    return await TherapistDataCRUD.add_note(current_therapist.id, client_id, content)


@router.get("/therapistInfo")
async def get_info(
        _: CurrentConfirmed,
        therapist_id: Annotated[int, Query()]
) -> TherapistInfo | None:
    return await TherapistInfoCRUD.get_by(therapist_id=therapist_id)


@router.get("/therapistInfo/full")
async def get_info_full(
        _: CurrentConfirmed,
        therapist_id: Annotated[int, Query()]
) -> TherapistInfoFull | None:
    info = await TherapistInfoCRUD.get_by(therapist_id=therapist_id)
    pfp = await UserCRUD.get_pfp(therapist_id)
    therapist = await UserCRUD.get_by(id=therapist_id)

    return TherapistInfoFull(
        **(await TherapistInfo.from_tortoise_orm(info)).model_dump(),
        pfp=pfp,
        name=therapist.nickname
    )


@router.post("/therapistInfo")
async def create_info(
        current_confirmed: CurrentConfirmed,
        therapist_id: Annotated[int, Query()],
        price: Annotated[int, Form()],
        about: Annotated[str, Form()],
        education: Annotated[str, Form()],
        theme_ids: Annotated[str, Form()],
        work_hours: Annotated[str, Form()]
) -> TherapistInfo | None:
    if await TherapistInfoCRUD.get_by(therapist_id=therapist_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already exists"
        )

    return await TherapistInfoCRUD.model.create(
        therapist_id=therapist_id,
        price=price,
        about=about,
        education=education.split(";;"),
        theme_ids=[int(el) for el in theme_ids.split(";")],
        work_hours=work_hours.split(";")
    )


@router.put("/therapistInfo/workHours")
async def update_work_hours(
    current_therapist: CurrentTherapist, work_hours: Annotated[str, Form()]
):
    return await TherapistInfoCRUD.update_by(
        dict(
            work_hours=[datetime.datetime.fromisoformat(iso) for iso in work_hours.split(";")]
        ),
        therapist_id=current_therapist.id
    )
