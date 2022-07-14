from unicodedata import decimal
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.contrib.postgres import fields as psqlfields
from django.db import models

# ------------------------- #

class Order(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    order_id = models.CharField(max_length=100, unique=True)
    index_number = models.IntegerField(unique=True)
    delivery_date = models.DateField()
    price_USD = models.DecimalField(max_digits=20, decimal_places=2)
    price_RUB = models.DecimalField(max_digits=20, decimal_places=2)
    delivery_expired = models.BooleanField()
    notification_sent = models.BooleanField(default=False)
    
    # ......................... #

    class Meta:
        ordering = ('index_number',)

# ------------------------- #