from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    quantity_needed = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "item_name",
            "category",
            "quantity_required",
            "quantity_have",
            "quantity_needed",
            "status",
        ]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}