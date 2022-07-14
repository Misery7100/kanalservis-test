from django.utils.timezone import now
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from googlesheets.models import Order

# ------------------------- #

class TicketSerializer(ModelSerializer):
    delivery_expired = SerializerMethodField()

    # ......................... #

    class Meta:
        model = Order
        fields = '__all__'
    
    # ......................... #
    
    def get_delivery_expired(self, obj):
        return (now - obj.delivery_date).days < 0