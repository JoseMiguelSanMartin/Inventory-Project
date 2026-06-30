from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets

from .forms import SignUpForm, InventoryItemForm, InventoryQuantityFormSet
from .models import InventoryItem, DailyReport
from .serializers import InventoryItemSerializer

manager_required = user_passes_test(lambda user: user.is_staff)

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
    query = request.GET.get("q", "")
    items = InventoryItem.objects.filter(item_name__icontains=query) if query else InventoryItem.objects.all()
    return render(request, "inventory/inventory_list.html", {"items": items, "query": query})

@login_required
@manager_required
def inventory_create(request):
    form = InventoryItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@login_required
@manager_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_form.html", {"form": form})


@login_required
@manager_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item.delete()
        return redirect("inventory_list")

    return render(request, "inventory/inventory_confirm_delete.html", {"item": item})


@login_required
@manager_required
def daily_report(request):
    queryset = InventoryItem.objects.all().order_by("item_name")
    formset = InventoryQuantityFormSet(request.POST or None, queryset=queryset)

    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            DailyReport.objects.create(submitted_by=request.user)
            return redirect("daily_report")
    
    total_fields = len(formset.forms)
    valid_fields = sum(
        1 for form in formset.forms
        if form.is_bound and not form.errors
    ) if request.method == "POST" else 0

    progress_percentage = int((valid_fields / total_fields) * 100) if total_fields > 0 else 0

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

    latest_report = DailyReport.objects.order_by("-submitted_at").first()

    return render(request, "inventory/daily_report.html", {
        "formset": formset,
        "items": queryset,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "complete": complete,
        "latest_report": latest_report,
        "progress": progress_percentage,
    })


@login_required
@manager_required
def api_docs(request):
    return render(request, "inventory/api_docs.html")


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
