import logging

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Dict

from googlesheets.models import Order
from googlesheets.serializers import OrderSerializer

# ------------------------- #

logger = logging.getLogger(__name__)

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_all_orders(request: Request) -> Response:

    queryset = Order.objects.all()
    serializer = OrderSerializer(queryset, many=True)

    return Response(status=status.HTTP_200_OK, data=serializer.data)

# ------------------------- #

def get_accum_price_in_time(currency: str) -> Dict[str, str]:

    assert currency in ["USD", "RUB"]

    queryset = (Order.objects
        .values('delivery_date')
        .order_by('delivery_date')
        .annotate(total=Sum(f"price_{currency}"))
    )

    result = tuple(queryset)

    result = dict( 
        (x['delivery_date'].strftime('%d.%m.%Y'), float(x['total']))
        for x in result
    )

    return result

# ------------------------- #

def get_total_price(currency: str) -> float:

    assert currency in ["USD", "RUB"]

    queryset = Order.objects.aggregate(Sum(f'price_{currency}'))
    total = queryset[f'price_{currency}__sum']

    return total

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_accum_price_usd_in_time(request: Request) -> Response:
    
    data = get_accum_price_in_time("USD")

    return Response(status=status.HTTP_200_OK, data=data)

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_accum_price_rub_in_time(request: Request) -> Response:
    
    data = get_accum_price_in_time("RUB")

    return Response(status=status.HTTP_200_OK, data=data)

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_total_price_usd(request: Request) -> Response:

    total = get_total_price("USD")

    return Response(status=status.HTTP_200_OK, data={"total" : total})

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_total_price_rub(request: Request) -> Response:

    total = get_total_price("RUB")

    return Response(status=status.HTTP_200_OK, data={"total" : total})