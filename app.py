"""Flask app which exposes a REST API around the fireworks calendar"""

import datetime
import http
import os
import typing

import flask

import scraper

app = flask.Flask(__name__)


class EventData(typing.TypedDict):
    """JSON-able object representing an event"""
    start: str
    end: str
    timeZone: str


def event_to_json(event: scraper.Event) -> EventData:
    return {
        'start': event.start.isoformat(),
        'end': event.end.isoformat(),
        'timeZone': event.timezone.key,
    }


def make_event_response(date: datetime.date) -> flask.Response:
    if event := scraper.get_event_for_day(date):
        return flask.make_response(event_to_json(event))
    else:
        return flask.make_response('', http.HTTPStatus.NOT_FOUND)


@app.route('/day/<date_str>')
def get_scheduled_at_date(date_str: str) -> flask.Response:
    """Query for a specific date"""
    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError as e:
        return flask.make_response(e, http.HTTPStatus.BAD_REQUEST)

    return make_event_response(date)


@app.route('/today')
def get_scheduled_today() -> flask.Response:
    """Query for today (in US/Eastern timezone)"""
    return make_event_response(datetime.date.today())


def whole_week() -> typing.Iterator[datetime.date]:
    today = datetime.date.today()
    for day_delta in range(7):
        yield today + datetime.timedelta(days=day_delta)


@app.route('/week')
def get_scheduled_week() -> list[EventData]:
    """Query for a whole week (in US/Eastern timezone)"""
    return [
        event_to_json(event)
        for event in scraper.get_events_for_days(whole_week())
    ]


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
