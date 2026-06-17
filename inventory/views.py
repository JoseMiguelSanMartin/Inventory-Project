from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets

from .forms import SignUpForm, InventoryItemForm
from .models import InventoryItem, DailyReport
from .serializers import InventoryItemSerializer


def home(request):
    return render(request, "inventory/home.html")


def signup(request):
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("inventory_list")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, "inventory/inventory_list.html", {"items": items})


@login_required
def inventory_create(request):
    form = InventoryItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@login_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item.delete()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_confirm_delete.html", {"item": item})


@login_required
def submit_daily_report(request):
    if request.method == "POST":
        DailyReport.objects.create(submitted_by=request.user)
        return redirect("daily_report")

    return redirect("inventory_list")


@login_required
def daily_report(request):
    items = InventoryItem.objects.all()

    out_of_stock = []
    low_stock = []
    complete = []

    for item in items:
        if item.quantity_have == 0:
            out_of_stock.append(item)
        elif item.quantity_needed > 0:
            low_stock.append(item)
        else:
            complete.append(item)

    latest_report = DailyReport.objects.order_by("-submitted_at").first()

    return render(request, "inventory/daily_report.html", {
        "items": items,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "complete": complete,
        "latest_report": latest_report,
    })


@login_required
def api_docs(request):
    return render(request, "inventory/api_docs.html")


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
