from django.urls import include, path

from googlesheets.views import *

# ------------------------- #

urlpatterns = [
    path('get-all-orders', get_all_orders, name='get-all-orders'),
    path('get-accum-price/usd', get_accum_price_usd_in_time, name='get-accum-price-usd'),
    path('get-accum-price/rub', get_accum_price_rub_in_time, name='get-accum-price-rub'),
    path('get-total-price/usd', get_total_price_usd, name='get-total-price-usd'),
    path('get-total-price/rub', get_total_price_rub, name='get-total-price-rub'),
]