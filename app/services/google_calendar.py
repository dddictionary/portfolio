import logging
import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("backend")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def create_event(
    *,
    summary: str,
    description: str,
    start: datetime,
    duration_min: int,
    timezone: str,
    attendee_email: str,
    attendee_name: str,
) -> str:
    service = build("calendar", "v3", credentials=_credentials(), cache_discovery=False)
    end = start + timedelta(minutes=duration_min)
    body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end.isoformat(), "timeZone": timezone},
        "attendees": [{"email": attendee_email, "displayName": attendee_name}],
        "reminders": {"useDefault": True},
    }
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    event = (
        service.events()
        .insert(calendarId=calendar_id, body=body, sendUpdates="all")
        .execute()
    )
    logger.info("Created calendar event id=%s", event["id"])
    return event["id"]
