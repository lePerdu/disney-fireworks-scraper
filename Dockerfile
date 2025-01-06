FROM python:3.11-alpine

ENV PYTHONUNBUFFERED True

RUN apk add --no-cache chromium chromium-chromedriver xvfb

WORKDIR /app
COPY requirements.txt /app/

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src/* /app/

CMD ["python", "/app/disney_fireworks_scraper/caldav_calendar.py"]
