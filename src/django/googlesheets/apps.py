import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate

# ------------------------- #

logger = logging.getLogger(__name__)

# ------------------------- #

def init_data_and_exchange_rate(sender: AppConfig, **kwargs) -> None:
    """
    Initialize data and exchange rate after migration.
    """

    from googlesheets.tasks import update_USD_exchange_rate, update_table_from_sheet

    update_USD_exchange_rate.apply_async()
    update_table_from_sheet.apply_async(countdown=1)

# ------------------------- #

def update_chat_id_telegram_bot() -> None:
    """
    Update chat ID with last value for testing purposes.
    """

    import os
    import json
    import requests
    
    url = f"https://api.telegram.org/bot{os.environ['TG_BOT_TOKEN']}/getUpdates"
    response = requests.get(url)
    data = response.json()

    messages = tuple(filter(lambda x: 'message' in x.keys(), data['result']))
    subscriptions = tuple(filter(lambda x: x['message']['text'] == '/subscribe', messages))
    max_datetime = sorted(subscriptions, key=lambda x: x['message']['date'], reverse=True)[0]

    new_chat_id = str(max_datetime['message']['chat']['id'])

    os.environ['TG_BOT_CHAT_ID'] = new_chat_id

# ------------------------- #

def get_or_create_scheduled_tasks(sender: AppConfig, **kwargs) -> None:
    """
    Configure scheduled tasks using celery.
    """

    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

    # construct schedule objects
    interval_15s, _ = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.SECONDS,
        )
    interval_15m, _ = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.MINUTES,
        )
    
    interval_3h, _ = IntervalSchedule.objects.get_or_create(
            every=3,
            period=IntervalSchedule.HOURS,
        )
    crontab_midnight, _ = CrontabSchedule.objects.get_or_create(
            minute=0, 
            hour=0
        )
    crontab_9am, _ = CrontabSchedule.objects.get_or_create(
            minute=0, 
            hour=9
        )

    # interval tasks
    PeriodicTask.objects.get_or_create(
        interval=interval_15s,
        name='googlesheets.tasks.update_table_from_sheet',
        task='googlesheets.tasks.update_table_from_sheet'
    )
    PeriodicTask.objects.get_or_create(
        interval=interval_15s,
        name='googlesheets.tasks.notify_about_expired_delivery',
        task='googlesheets.tasks.notify_about_expired_delivery'
    )

    # crontab scheduled tasks
    PeriodicTask.objects.get_or_create(
        crontab=crontab_midnight,
        name='googlesheets.tasks.reset_notification_status',
        task='googlesheets.tasks.reset_notification_status'
    )
    PeriodicTask.objects.get_or_create(
        crontab=crontab_9am,
        name='googlesheets.tasks.update_USD_exchange_rate',
        task='googlesheets.tasks.update_USD_exchange_rate'
    )

# ------------------------- #

class GooglesheetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'googlesheets'

    # ......................... #

    def ready(self) -> None:

        # update chat id
    
        update_chat_id_telegram_bot()

        # link post migrate state and function calls

        post_migrate.connect(get_or_create_scheduled_tasks, sender=self)
        post_migrate.connect(init_data_and_exchange_rate, sender=self)
