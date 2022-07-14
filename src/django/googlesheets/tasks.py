import gspread
import logging
import os
import requests
import xmltodict

from django.utils.timezone import now
from dateutil import parser as dtparser
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

from backend.celery.celery import app as celery_app

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent.parent # src
logger = logging.getLogger(__name__)

# ------------------------- #

@celery_app.task
def update_table_from_sheet(sheet_name: str = "kanalservis-test"):

    from googlesheets.models import Order

    key_replace = {
        "№": "index_number",
        "заказ №": "order_id",
        "стоимость, $": "price_USD",
        "срок поставки" : "delivery_date"
    }

    scope = (
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    )

    credspath = os.path.join(BASE_DIR, "secret/creds.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(credspath, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()

    data = [
        dict((key_replace[key], value) for key, value in row.items()) 
        for row in data 
        if not ('' in row.values())
    ]

    for row in data:
        row['delivery_date'] = dtparser.parse(row['delivery_date'])
        row['delivery_expired'] = (row['delivery_date'] - now().replace(tzinfo=None)).days < 0
        row['delivery_date'] = row['delivery_date'].strftime(format="%Y-%m-%d")
        row['price_RUB'] = float(os.environ['USD_EXCHANGE_RATE']) * row['price_USD']

    data = [Order(**row) for row in data]

    Order.objects.bulk_update_or_create(
        data, 
        update_fields=('index_number', 'delivery_expired', 'price_USD', 'price_RUB', 'order_id'),
        match_field='order_id'
    )

# ------------------------- #

@celery_app.task
def notify_about_expired_delivery():
    
    import telegram
    import prettytable as pt
    from googlesheets.models import Order

    expired_no_notified = Order.objects.filter(
        delivery_expired=True,
        notification_sent=False
    )

    message_content = dict()

    for row in expired_no_notified:
        row.notification_sent = True
        message_content[row.order_id] = -(row.delivery_date - now().date()).days
        row.save()
    
    if message_content:

        table = pt.PrettyTable(['Заказ №', 'Дней назад'])
        table.align['Order ID'] = 'l'
        table.align['Days overdue'] = 'l'

        message_content = sorted(message_content.items(), key=lambda x: x[1], reverse=True)

        for row in message_content:
            table.add_row(row)
        
        bot = telegram.Bot(token=os.environ['TG_BOT_TOKEN'])
        bot.sendMessage(
            chat_id=os.environ['TG_BOT_CHAT_ID'], 
            text=f'<b>Несоблюдение срока поставки</b>\n\n<pre>{table}</pre>', 
            parse_mode=telegram.ParseMode.HTML
        )

# ------------------------- #

@celery_app.task
def reset_notification_status():

    from googlesheets.models import Order

    expired = Order.objects.filter(
        delivery_expired=True
    )

    for row in expired:
        row.notification_sent = False
        row.save()

# ------------------------- #

@celery_app.task
def update_USD_exchange_rate():

    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
    tree = xmltodict.parse(response.content)
    usd = filter(lambda x: x['@ID'] == 'R01235', tree['ValCurs']['Valute'])
    exchange_rate = tuple(usd)[0]['Value'].replace(',', '.')

    os.environ['USD_EXCHANGE_RATE'] = exchange_rate

    return f"current exchange rate: {os.environ['USD_EXCHANGE_RATE']} RUB in 1 USD"

# ------------------------- #