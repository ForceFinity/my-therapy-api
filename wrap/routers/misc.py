__tags__ = ["misc"]
__prefix__ = "/misc"

import json
import os.path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from wrap.applications.user import User, get_current_user, RefereedCRUD, UserCRUD
from wrap.applications.user.schemas import Refereed
from wrap.core.utils import crypto

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
ANSWERS_SPREADSHEET = "1ycxADvDRgkCHsuu74426eFsi6oEjxiSo6NH3vvF-Lz0"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

emails_range = "B2:B"
credentials_file = "token.json"
cache_file = "emails.json"

router = APIRouter()


def get_emails() -> list | None:
    creds = None
    emails = json.dumps(cache_file)
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(credentials_file):
        creds = Credentials.from_authorized_user_file(credentials_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(credentials_file, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()

        result = (
            sheet.values()
            .get(spreadsheetId=ANSWERS_SPREADSHEET, range=emails_range)
            .execute()
        )
        values = [v[0] for v in result.get("values", [])]

        return values if values else None

    except HttpError as err:
        print(err)


@router.get("/verifyQuestionnaireCompletion/")
async def verify_questionnaire_completion(
        current_user: Annotated[User, Depends(get_current_user)]
) -> bool:
    if not (emails := get_emails()):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong with the spreadsheet"
        )

    if current_user.email not in emails:
        return False

    await UserCRUD.update_by({"is_questionnaire_complete": True}, id=current_user.id)

    if record := await RefereedCRUD.get_by(refereed_id=current_user.id):
        await RefereedCRUD.update_by({"is_questionnaire_complete": True}, id=record.id)

    return True


@router.get("/verifyAllQuestionnaire")
async def verify_all_questionnaire(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.email != "hexchap@gmail.com":
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin only"
        )
    emails = get_emails()

    for user in await UserCRUD.get_all():
        if user.email not in emails:
            continue

        await UserCRUD.update_by({"is_questionnaire_complete": True}, id=user.id)

        if record := await RefereedCRUD.get_by(refereed_id=user.id):
            await RefereedCRUD.update_by({"is_questionnaire_complete": True}, id=record.id)


@router.get("/")
async def test():
    return crypto.phone_hotp.at(11)


@router.get("/getRefereed")
async def get_refereed(
        current_user: Annotated[User, Depends(get_current_user)]
):
    resp = []

    for refereed in await RefereedCRUD.model.filter(user_id=current_user.id).all():
        refereed = await refereed.refereed

        if refereed.is_confirmed:
            resp.append({
                "email": (await refereed).email,
                "is_questionnaire_complete": (await refereed).is_questionnaire_complete,
            })

    return resp
