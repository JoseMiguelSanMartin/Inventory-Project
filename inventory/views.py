from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import ExpressionWrapper, F, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .forms import SignUpForm, InventoryItemForm, InventoryQuantityFormSet
from .models import InventoryItem, DailyReport, DailyReportSnapshot
from .serializers import InventoryItemSerializer


def _is_manager(user):
    return (
        user.is_active
        and user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )
    )

manager_required = user_passes_test(_is_manager, login_url="login")


def home(request):
    if request.user.is_authenticated:
        return redirect("inventory_list")
    return render(request, "inventory/home.html")


@login_required
@manager_required
def signup(request):
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("inventory_list")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def inventory_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    qty_needed_expr = ExpressionWrapper(
        F("quantity_required") - F("quantity_have"),
        output_field=IntegerField(),
    )
    items = InventoryItem.objects.annotate(qty_needed_db=qty_needed_expr)

    if query:
        items = items.filter(item_name__icontains=query)

    if status == "complete":
        items = items.filter(qty_needed_db__lte=0)
    elif status == "missing":
        items = items.filter(qty_needed_db__gt=0)
    elif status == "out":
        items = items.filter(quantity_have=0)

    items = list(items)
    complete_count = sum(1 for item in items if item.quantity_needed == 0)
    missing_count = sum(1 for item in items if item.quantity_needed > 0)
    total_needed = sum(item.quantity_needed for item in items)

    return render(request, "inventory/inventory_list.html", {
        "items": items,
        "query": query,
        "status": status,
        "complete_count": complete_count,
        "missing_count": missing_count,
        "total_needed": total_needed,
    })


@manager_required
def inventory_create(request):
    form = InventoryItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item added successfully.")
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@manager_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item updated successfully.")
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@manager_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item.delete()
        messages.success(request, f"\"{item.item_name}\" was deleted.")
        return redirect("inventory_list")

    return render(request, "inventory/inventory_confirm_delete.html", {"item": item})


@manager_required
def daily_report(request):
    queryset = InventoryItem.objects.all().order_by("item_name")
    formset = InventoryQuantityFormSet(request.POST or None, queryset=queryset)

    if request.method == "POST":
        if formset.is_valid():
            updated_items = formset.save()

            report = DailyReport.objects.create(submitted_by=request.user)

            all_items = InventoryItem.objects.all()
            DailyReportSnapshot.objects.bulk_create([
                DailyReportSnapshot(
                    report=report,
                    item_name=item.item_name,
                    category=item.category,
                    quantity_required=item.quantity_required,
                    quantity_have=item.quantity_have,
                    quantity_needed=item.quantity_needed,
                    status=item.status,
                )
                for item in all_items
            ])

            messages.success(request, "Daily report submitted successfully.")
            return redirect("daily_report")
        else:
            messages.error(request, "Please fix the errors below before submitting.")

    total_fields = len(formset.forms)
    valid_fields = sum(
        1 for form in formset.forms
        if form.is_bound and not form.errors
    ) if request.method == "POST" else 0

    progress_percentage = int((valid_fields / total_fields) * 100) if total_fields > 0 else 0

    selected_date = request.GET.get("date", "")
    reports = DailyReport.objects.all().order_by("-submitted_at")
    if selected_date:
        reports = reports.filter(submitted_at__date=selected_date)
    latest_report = reports.first()

    out_of_stock = []
    low_stock = []
    complete = []

    for item in queryset:
        if item.quantity_have == 0:
            out_of_stock.append(item)
        elif item.quantity_needed > 0:
            low_stock.append(item)
        else:
            complete.append(item)

    total_issues = len(out_of_stock) + len(low_stock)

    return render(request, "inventory/daily_report.html", {
        "formset": formset,
        "items": queryset,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "complete": complete,
        "latest_report": latest_report,
        "progress": progress_percentage,
        "reports": reports,
        "selected_date": selected_date,
        "total_issues": total_issues,
    })


@manager_required
def daily_report_detail(request, pk):
    report = get_object_or_404(DailyReport, pk=pk)
    snapshots = report.snapshots.all()
    out_of_stock = [s for s in snapshots if s.quantity_have == 0]
    low_stock = [s for s in snapshots if s.quantity_have > 0 and s.quantity_needed > 0]
    complete = [s for s in snapshots if s.quantity_needed == 0]
    total_issues = len(out_of_stock) + len(low_stock)

    return render(request, "inventory/daily_report_detail.html", {
        "report": report,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "complete": complete,
        "total_issues": total_issues,
    })


@manager_required
def api_docs(request):
    return render(request, "inventory/api_docs.html")


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]