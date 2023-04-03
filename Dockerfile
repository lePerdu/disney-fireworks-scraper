FROM python:3.11-alpine

ENV PYTHONUNBUFFERED True

RUN apk add --no-cache chromium chromium-chromedriver xvfb-run dumb-init

WORKDIR /app
COPY requirements.txt /app/

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY scraper.py app.py /app/

CMD dumb-init xvfb-run gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
