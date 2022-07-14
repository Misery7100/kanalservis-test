FROM python:3.8-slim

# optional
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/kanalservis_test

# optional
RUN apt-get update
RUN mkdir -pv /var/{log,run}/gunicorn/

# copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

# copy start scripts
COPY ./backend/celery/start-worker start-worker
RUN chmod +x start-worker

COPY ./backend/celery/start-beat start-beat
RUN chmod +x start-beat

COPY ./gunicorn/dev/start start-dev
RUN chmod +x start-dev