FROM python:3.11-alpine

ENV PYTHONUNBUFFERED True

RUN apk add --no-cache chromium chromium-chromedriver xvfb-run dumb-init

WORKDIR /app
COPY requirements.txt /app/

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src/* /app/

ENTRYPOINT ["dumb-init", "xvfb-run"]
CMD ["python", "google_calendar.py"]
