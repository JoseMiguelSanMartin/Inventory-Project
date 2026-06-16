from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    quantity_needed = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = ["id", "item_name", "quantity_required", "quantity_have", "quantity_needed"]
