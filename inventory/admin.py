from django.contrib import admin
from .models import InventoryItem, DailyReport, DailyReportSnapshot


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "category", "quantity_required", "quantity_have", "status")
    list_filter = ("category",)
    search_fields = ("item_name",)


class DailyReportSnapshotInline(admin.TabularInline):
    model = DailyReportSnapshot
    extra = 0
    readonly_fields = ("item_name", "category", "quantity_required", "quantity_have", "quantity_needed", "status")
    can_delete = False


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("__str__", "submitted_by", "submitted_at")
    inlines = [DailyReportSnapshotInline]