from rest_framework.serializers import ModelSerializer

from googlesheets.models import Order

# ------------------------- #

class OrderSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = (
            'index_number',
            'order_id',
            'price_USD',
            'price_RUB',
            'delivery_date'
        )