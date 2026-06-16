from django.db import models

class InventoryItem(models.Model):
    item_name = models.CharField(max_length=100)
    quantity_required = models.PositiveIntegerField(default=0)
    quantity_have = models.PositiveIntegerField(default=0)

    @property
    def quantity_needed(self):
        return max(0, self.quantity_required - self.quantity_have)

    def __str__(self):
        return self.item_name
