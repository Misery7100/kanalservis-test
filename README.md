# Kanalservis test task

Dockerized app for pulling and manipulating data from Google Sheets via Google API. Based on Django and Celery.

## Features

- Auto pull data every 15 seconds from following sheet: [click](https://docs.google.com/spreadsheets/d/1_aOcWJJ2FWhfAp1dBEOAyrV8iNsqNLT8j7l-PcjarCU/edit#gid=0)
- Ignore empty fields in the data (according to initial format)
- Doesn't work with duplications by order ID or index number (№) due nature of create or update functionality - impossible to resolve duplication conflict for unique keys
- Auto update USDRUB exchange rate via CBR XML script every day at 9:00
- Telegram Bot notifications for expired orders implemented as bulk interval message every 15 minutes single time per day for every expired order (auto-reset notification state at 00:00 every day)

## Requirements

1. Install `docker, docker-compose`
2. Copy .env file data using following onetimesecret (WORKS ONLY ONCE!): [click](https://onetimesecret.com/secret/p9qb8bnuraj7r0v3ik2m9nctgg7v3vn)
3. Create file `src/django/secret/.env` and paste data
4. Copy GCP credentials data using another onetimesecret (WORKS ONLY ONCE!):[click](https://onetimesecret.com/secret/b1d1romws4jyj1yujs02yrx2jbu0bzc)
5. Create file `src/django/secret/creds.json` and paste data
6. Start chat with bot `kanalservistest_bot` and send message `/subscribe` to receive notifications

### Notes: 

- Since it test task bot uses only last chat ID where `/subscribe` message occurs
- This annoying steps with manual secure data re-creation caused by the impossibility to communicate/connect with task inspectors via HR bot

## Usage

### Start app

Move to the source dir:

```bash
cd src
```

```bash
docker-compose up --build
```

or in detached mode

```bash
docker-compose up --build -d
```

PostgreSQL database will be available for observe at `5433` port, Django app accepts requests at `8000` port. 

### Get all orders

To query all elements from a database table Order, open `http://localhost:8000/sheets/get-all-orders` or make request with curl:

```bash
curl http://localhost:8000/sheets/get-all-orders
```

### Get aggregated price in time

For USD:

```bash
curl http://localhost:8000/sheets/get-accum-price/usd
```

For RUB:

```bash
curl http://localhost:8000/sheets/get-accum-price/rub
```

### Get total price

For USD:

```bash
curl http://localhost:8000/sheets/get-total-price/usd
```

For RUB:

```bash
curl http://localhost:8000/sheets/get-total-price/rub
```

### Kill app

```bash
docker-compose down
```

