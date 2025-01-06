import datetime
import logging
import os.path
import typing
from collections.abc import Iterator

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import disney_fireworks_scraper as scraper

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = (
    "da5bef1e62a846bfa5ae217324f3766ca1f4736514e05b6fdbb29dd76919d91c"
    "@group.calendar.google.com"
)
EVENT_NAME = "Magic Kingdom Fireworks"
EVENT_TIMEZONE = "US/Eastern"

CalendarService = typing.Any


def get_service() -> CalendarService:
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds is None or not creds.valid:
        if creds is not None and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            _ = token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def event_exists(service: CalendarService, event: scraper.Event) -> bool:
    # TODO: Seach in whole day in case the scheduled time changes?
    found = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            q=EVENT_NAME,
            timeMin=event.start.isoformat(),
            timeMax=event.end.isoformat(),
            timeZone=event.timezone.key,
            maxResults=1,
        )
        .execute()
    )
    if len(found["items"]) > 0:
        logging.info(f"Event already exists: {event}")
        return True
    else:
        return False


def create_event(service: CalendarService, event: scraper.Event):
    # TODO: Check for event _before_ scraping the event time?
    # TODO: Check for existing event
    logging.info(f"Creating event {event}")
    service.events().insert(
        calendarId=CALENDAR_ID,
        body={
            "summary": EVENT_NAME,
            "start": {
                "timeZone": event.timezone.key,
                "dateTime": event.start.isoformat(),
            },
            "end": {
                "timeZone": event.timezone.key,
                "dateTime": event.end.isoformat(),
            },
        },
    ).execute()
    logging.info(f"Created event {event}")


def create_if_missing(service: CalendarService, event: scraper.Event):
    if event_exists(service, event):
        return
    create_event(service, event)


def whole_week() -> Iterator[datetime.date]:
    today = datetime.date.today()
    for day_delta in range(7):
        yield today + datetime.timedelta(days=day_delta)


def main():
    service = get_service()
    for event in scraper.get_events_for_days(whole_week()):
        create_if_missing(service, event)


if __name__ == "__main__":
    main()
