from django.apps import AppConfig
from django.db.models.signals import post_migrate

# ------------------------- #

def init_data_and_exchange_rate(sender: AppConfig, **kwargs) -> None:

    from googlesheets.tasks import update_USD_exchange_rate, update_table_from_sheet

    update_USD_exchange_rate.apply_async()
    update_table_from_sheet.apply_async(countdown=1)

# ------------------------- #

def schedule_data_update(sender: AppConfig, **kwargs) -> None:
    """
    Configure ... with celery and django_celery_beat.
    """

    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

    interval_15s, _ = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.SECONDS,
        )
    interval_15min, _ = IntervalSchedule.objects.get_or_create(
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

    # interval
    PeriodicTask.objects.get_or_create(
        interval=interval_15s,
        name='googlesheets.tasks.update_table_from_sheet',
        task='googlesheets.tasks.update_table_from_sheet'
    )
    PeriodicTask.objects.get_or_create(
        interval=interval_3h,
        name='googlesheets.tasks.update_USD_exchange_rate',
        task='googlesheets.tasks.update_USD_exchange_rate'
    )
    # PeriodicTask.objects.get_or_create(
    #     interval=interval_15m,
    #     name='googlesheets.tasks.notify_about_expired_delivery',
    #     task='googlesheets.tasks.notify_about_expired_delivery'
    # )

    # crontab
    PeriodicTask.objects.get_or_create(
        crontab=crontab_midnight,
        name='googlesheets.tasks.reset_notification_status',
        task='googlesheets.tasks.reset_notification_status'
    )

# ------------------------- #

class GooglesheetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'googlesheets'

    # ......................... #

    def ready(self) -> None:
        post_migrate.connect(schedule_data_update, sender=self)
        post_migrate.connect(init_data_and_exchange_rate, sender=self)
