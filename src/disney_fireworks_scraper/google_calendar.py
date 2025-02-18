import datetime
import logging
import os
import typing
from collections.abc import Iterator

from googleapiclient.discovery import build, service_account
from xvfbwrapper import Xvfb

from . import scraper

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = (
    "da5bef1e62a846bfa5ae217324f3766ca1f4736514e05b6fdbb29dd76919d91c"
    "@group.calendar.google.com"
)
EVENT_NAME = "Magic Kingdom Fireworks"
EVENT_TIMEZONE = "US/Eastern"

CalendarService = typing.Any

CALENDAR_ID = os.environ.get("CALENDAR_ID")
assert CALENDAR_ID is not None

CREDENTIALS_FILE = os.environ.get("CREDENTIALS_FILE", "credentials.json")


def get_service() -> CalendarService:
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
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
    with Xvfb():
        cal = get_service()
        for event in scraper.get_events_for_days(whole_week()):
            create_if_missing(cal, event)


if __name__ == "__main__":
    main()
