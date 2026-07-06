from django.contrib.auth.models import User
from django.db import models

class InventoryItem(models.Model):
    ITEM_CHOICES = [
        ("Gloves Set", "Gloves Set"),
        ("Hose Head", "Hose Head"),
        ("Knee Pad Set", "Knee Pad Set"),
        ("Pro Grip", "Pro Grip"),
        ("Orange Soap", "Orange Soap"),
        ("Mini Roller", "Mini Roller"),
        ("Paver", "Paver"),
        ("Mini Brushes", "Mini Brushes"),
        ("Scrapers", "Scrapers"),
        ("Flat Head", "Flat Head"),
        ("Scissors", "Scissors"),
        ("Bottle", "Bottle"),
        ("Brushes", "Brushes"),
        ("Buckets", "Buckets"),
        ("Sealing Buckets", "Sealing Buckets"),
        ("Rocks", "Rocks"),
        ("Masks", "Masks"),
        ("Guns", "Guns"),
        ("Battery", "Battery"),
        ("Safety Glasses", "Safety Glasses"),
        ("New Brushes", "Brushes"),
        ("Clear Seal Bucket", "Clear Seal Bucket"),
        ("Garbage Bags", "Garbage Bags"),
        ("Heads for Roller", "Heads for Roller"),
        ("Head for Mini Roller", "Head for Mini Roller"),
        ("Respirator", "Respirator"),
        ("Pebbles", "Pebbles"),
        ("Crack Fill", "Crack Fill"),
    ]

    item_name = models.CharField(max_length=100, choices=ITEM_CHOICES)
    quantity_required = models.PositiveIntegerField(default=0)
    quantity_have = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def quantity_needed(self):
        return max(0, self.quantity_required - self.quantity_have)

    def __str__(self):
        return self.item_name
    
    @property
    def status(self):
        if self.quantity_have == 0:
            return "Out of Stock"
        elif self.quantity_needed > 0:
            return "Low Stock"
        return "Complete"

class DailyReport(models.Model):
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Daily Report - {self.submitted_at.date()} by {self.submitted_by}"


class DailyReportSnapshot(models.Model):
    """
    Freezes the state of every InventoryItem at the moment a DailyReport
    is submitted.  Querying snapshots through a report gives you the
    historical picture rather than today's live quantities.
    """
    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    quantity_required = models.PositiveIntegerField()
    quantity_have = models.PositiveIntegerField()


    quantity_needed = models.PositiveIntegerField()
    status = models.CharField(max_length=20)

    class Meta:
        ordering = ["item_name"]

    def __str__(self):
        return f"{self.item_name} @ report #{self.report_id}"