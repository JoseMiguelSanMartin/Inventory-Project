from django.contrib.auth.models import User
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

class DailyReport(models.Model):
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Daily Report - {self.submitted_at.date()} by {self.submitted_by}"