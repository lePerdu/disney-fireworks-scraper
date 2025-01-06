import datetime
import json
import logging
import zoneinfo
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

SITE_URL = (
    "https://disneyworld.disney.go.com/entertainment/magic-kingdom"
    "/happily-ever-after-fireworks/"
)
# TODO Figure this out from the URL above somehow?
API_BASE_URL = (
    "https://disneyworld.disney.go.com/finder/api/v1/explorer-service"
    "/details-entity-schedule/wdw/18672598;entityType=Entertainment/"
)

DATE_FORMAT = "%A, %B %d, %Y"
TIME_FORMAT = "%H:%M:%S"

DISNEY_WORLD_TIMEZONE_NAME = "America/Detroit"
DISNEY_WORLD_TIMEZONE = zoneinfo.ZoneInfo(DISNEY_WORLD_TIMEZONE_NAME)

# The API payload contains a start and end time, but they are always
# the same, so the duration has to be hard-coded here.
EVENT_DURATION = datetime.timedelta(minutes=15)


@dataclass
class Event:
    start: datetime.datetime
    end: datetime.datetime
    timezone: zoneinfo.ZoneInfo


def create_browser() -> webdriver.Chrome:
    logging.info("Configuring browser instance")
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def make_api_url(date: datetime.date) -> str:
    return API_BASE_URL + str(date)


def parse_api_response(driver: webdriver.Chrome) -> Event | None:
    body = driver.find_element(By.TAG_NAME, "body")
    data = json.loads(body.text)
    schedules = data["schedule"]["schedules"]
    if "No Performance" in schedules:
        return None
    performance_obj = schedules["Performance Time"]
    # Disney's API keeps changing the field name, so just pick whatever single
    # field is there
    performances = list(performance_obj.values())
    if len(performances) != 1:
        raise Exception(
            f"Expected exactly 1 performance object. Got {len(performances)}"
        )
    performance_group = performances[0]
    event_data = performance_group[0]

    date = datetime.datetime.strptime(event_data["date"], "%Y-%m-%d").date()
    time = datetime.datetime.strptime(event_data["startTime"], "%H:%M:%S").time()
    start_datetime = datetime.datetime.combine(date, time, tzinfo=DISNEY_WORLD_TIMEZONE)
    return Event(
        start_datetime,
        start_datetime + EVENT_DURATION,
        DISNEY_WORLD_TIMEZONE,
    )


def get_events_for_days(days: Iterable[datetime.date]) -> Iterator[Event]:
    with create_browser() as driver:
        logging.info("Browser instance opened")
        driver.get(SITE_URL)
        # time.sleep(10)
        logging.info("Site opened")

        for day in days:
            driver.get(make_api_url(day))
            if event := parse_api_response(driver):
                yield event


def get_event_for_day(day: datetime.date) -> Event | None:
    # Hacky way to convert an iterator of 1 item into an optional
    for event in get_events_for_days((day,)):
        return event
    return None


if __name__ == "__main__":
    if event := get_event_for_day(datetime.date.today()):
        print("Scheduled at", event)
