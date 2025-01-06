#!/usr/bin/env python3

import datetime
import logging
import os
from collections.abc import Iterator

import caldav
import dotenv

from . import scraper

dotenv.load_dotenv()

CALDAV_URL = os.environ.get("CALDAV_URL")
assert CALDAV_URL is not None

CALDAV_USERNAME = os.environ.get("CALDAV_USERNAME")
assert CALDAV_USERNAME

CALDAV_PASSWORD = os.environ.get("CALDAV_PASSWORD")
assert CALDAV_PASSWORD

CALENDAR_ID = os.environ.get("CALENDAR_ID")
assert CALENDAR_ID

EVENT_NAME = os.environ.get("CALENDAR_EVENT_NAME", "Magic Kingdom Fireworks")
EVENT_TIMEZONE = os.environ.get("CALENDAR_TIMEZONE", "US/Eastern")


def get_client() -> caldav.Calendar:
    return (
        caldav.DAVClient(
            url=CALDAV_URL,
            username=CALDAV_USERNAME,
            password=CALDAV_PASSWORD,
        )
        .principal()
        .calendar(cal_id=CALENDAR_ID)
    )


def event_exists(cal: caldav.Calendar, event: scraper.Event) -> bool:
    # TODO: Seach in whole day in case the scheduled time changes?
    found = cal.search(
        summary=EVENT_NAME,
        start=event.start,
        end=event.end,
        event=True,
        expand=True,
    )
    if len(found) > 0:
        logging.info(f"Event already exists: {event}")
        return True
    else:
        return False


def create_event(cal: caldav.Calendar, event: scraper.Event):
    # TODO: Check for event _before_ scraping the event time?
    # TODO: Check for existing event
    logging.info(f"Creating event {event}")
    cal.save_event(
        summary=EVENT_NAME,
        dtstart=event.start,
        dtend=event.end,
    )
    logging.info(f"Created event {event}")


def create_if_missing(cal: caldav.Calendar, event: scraper.Event):
    if event_exists(cal, event):
        return
    create_event(cal, event)


def whole_week() -> Iterator[datetime.date]:
    today = datetime.date.today()
    for day_delta in range(7):
        yield today + datetime.timedelta(days=day_delta)


def main():
    cal = get_client()
    for event in scraper.get_events_for_days(whole_week()):
        create_if_missing(cal, event)


if __name__ == "__main__":
    main()
