from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import ExpressionWrapper, F, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .forms import InventoryItemForm, InventoryQuantityFormSet, SignUpForm
from .models import DailyReport, DailyReportSnapshot, InventoryItem
from .serializers import InventoryItemSerializer


def _is_manager(user):
    return (
        user.is_authenticated
        and user.is_active
        and (
            user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )
    )


manager_required = user_passes_test(_is_manager, login_url="login")


def _staff_access_allowed(user):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_staff or user.is_superuser)
    )


def send_daily_report_email(request, report, recipient_email):
    """
    Email a saved daily report to the selected recipient.

    The application Gmail account remains the sender. When the submitting
    staff member has an email address, replies are directed to that address.
    """
    snapshots = report.snapshots.all().order_by("item_name")

    out_of_stock = [
        item for item in snapshots
        if item.quantity_have == 0
    ]

    low_stock = [
        item for item in snapshots
        if item.quantity_have > 0 and item.quantity_needed > 0
    ]

    complete = [
        item for item in snapshots
        if item.quantity_needed == 0
    ]

    report_url = request.build_absolute_uri(
        reverse("daily_report_detail", args=[report.pk])
    )

    submitter_name = (
        report.submitted_by.get_full_name()
        or report.submitted_by.username
    )

    report_lines = [
        "A daily inventory report has been submitted.",
        "",
        f"Submitted by: {submitter_name}",
        f"Submitted at: {report.submitted_at:%B %d, %Y at %I:%M %p}",
        "",
        "REPORT SUMMARY",
        "------------------------------",
        f"Out of stock: {len(out_of_stock)}",
        f"Low stock: {len(low_stock)}",
        f"Complete: {len(complete)}",
        "",
    ]

    if out_of_stock:
        report_lines.extend([
            "OUT OF STOCK",
            "------------------------------",
        ])

        for item in out_of_stock:
            report_lines.append(
                f"- {item.item_name}: "
                f"Have {item.quantity_have}, "
                f"Required {item.quantity_required}, "
                f"Need {item.quantity_needed}"
            )

        report_lines.append("")

    if low_stock:
        report_lines.extend([
            "LOW STOCK",
            "------------------------------",
        ])

        for item in low_stock:
            report_lines.append(
                f"- {item.item_name}: "
                f"Have {item.quantity_have}, "
                f"Required {item.quantity_required}, "
                f"Need {item.quantity_needed}"
            )

        report_lines.append("")

    report_lines.extend([
        "View the complete report:",
        report_url,
    ])

    reply_to = [request.user.email] if request.user.email else None

    email = EmailMessage(
        subject=f"Daily Inventory Report - {report.submitted_at:%B %d, %Y}",
        body="\n".join(report_lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
        reply_to=reply_to,
    )
    email.send(fail_silently=False)


def home(request):
    if request.user.is_authenticated:
        return redirect("inventory_list")

    return render(request, "inventory/home.html")


@manager_required
def signup(request):
    """Managers can create users without being logged out of their own account."""
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        new_user = form.save()
        messages.success(
            request,
            f'User "{new_user.username}" was created successfully.',
        )
        return redirect("inventory_list")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def inventory_list(request):
    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    quantity_needed_expression = ExpressionWrapper(
        F("quantity_required") - F("quantity_have"),
        output_field=IntegerField(),
    )

    items = InventoryItem.objects.annotate(
        quantity_needed_db=quantity_needed_expression
    )

    if query:
        items = items.filter(item_name__icontains=query)

    if status == "complete":
        items = items.filter(quantity_needed_db__lte=0)
    elif status == "missing":
        items = items.filter(quantity_needed_db__gt=0)
    elif status == "out":
        items = items.filter(quantity_have=0)

    items = list(items)

    complete_count = sum(1 for item in items if item.quantity_needed == 0)
    missing_count = sum(1 for item in items if item.quantity_needed > 0)
    total_needed = sum(item.quantity_needed for item in items)

    return render(
        request,
        "inventory/inventory_list.html",
        {
            "items": items,
            "query": query,
            "status": status,
            "complete_count": complete_count,
            "missing_count": missing_count,
            "total_needed": total_needed,
        },
    )


@login_required
def inventory_create(request):
    if not _staff_access_allowed(request.user):
        messages.error(request, "Only staff members can add inventory items.")
        return redirect("inventory_list")

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

    return render(
        request,
        "inventory/inventory_form.html",
        {"form": form, "item": item},
    )


@manager_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item_name = item.item_name
        item.delete()
        messages.success(request, f'"{item_name}" was deleted.')
        return redirect("inventory_list")

    return render(
        request,
        "inventory/inventory_confirm_delete.html",
        {"item": item},
    )


@login_required
def submit_daily_report(request):
    """
    Preserve the old URL without creating a report that has no selected
    recipient. All report submissions now happen on the daily-report page.
    """
    if not _staff_access_allowed(request.user):
        messages.error(request, "Only staff members can submit daily reports.")
        return redirect("inventory_list")

    messages.info(
        request,
        "Choose an email recipient before submitting the report.",
    )
    return redirect("daily_report")


@login_required
def daily_report(request):
    """
    Allow normal staff, managers, and superusers to update inventory,
    choose an approved recipient, save a report snapshot, and email it.
    """
    if not _staff_access_allowed(request.user):
        messages.error(request, "Only staff members can submit daily reports.")
        return redirect("inventory_list")

    User = get_user_model()
    inventory_queryset = InventoryItem.objects.all().order_by("item_name")

    email_recipients = (
        User.objects
        .filter(is_active=True)
        .exclude(email="")
        .order_by("first_name", "last_name", "username")
    )

    formset = InventoryQuantityFormSet(
        request.POST or None,
        queryset=inventory_queryset,
    )

    selected_recipient = ""

    if request.method == "POST":
        selected_recipient = request.POST.get("recipient_email", "").strip()
        recipient_is_valid = True

        try:
            validate_email(selected_recipient)
        except ValidationError:
            recipient_is_valid = False
            messages.error(request, "Please select a valid email recipient.")

        if recipient_is_valid:
            recipient_exists = email_recipients.filter(
                email__iexact=selected_recipient
            ).exists()

            if not recipient_exists:
                recipient_is_valid = False
                messages.error(
                    request,
                    "The selected recipient is not an approved active user.",
                )

        if recipient_is_valid and formset.is_valid():
            formset.save()

            report = DailyReport.objects.create(submitted_by=request.user)
            current_items = InventoryItem.objects.all()

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
                for item in current_items
            ])

            try:
                send_daily_report_email(
                    request=request,
                    report=report,
                    recipient_email=selected_recipient,
                )
            except Exception as error:
                messages.warning(
                    request,
                    "The report was saved, but the email could not be sent. "
                    f"Email error: {error}",
                )
            else:
                messages.success(
                    request,
                    "Daily report submitted and emailed to "
                    f"{selected_recipient}.",
                )

            return redirect("daily_report_detail", pk=report.pk)

        if recipient_is_valid and not formset.is_valid():
            messages.error(
                request,
                "Please correct the inventory errors before submitting.",
            )

    total_fields = len(formset.forms)
    valid_fields = (
        sum(
            1
            for form in formset.forms
            if form.is_bound and not form.errors
        )
        if request.method == "POST"
        else 0
    )

    progress_percentage = (
        int((valid_fields / total_fields) * 100)
        if total_fields > 0
        else 0
    )

    selected_date = request.GET.get("date", "").strip()
    reports = DailyReport.objects.all().order_by("-submitted_at")

    if selected_date:
        reports = reports.filter(submitted_at__date=selected_date)

    latest_report = reports.first()
    out_of_stock = []
    low_stock = []
    complete = []

    for item in inventory_queryset:
        if item.quantity_have == 0:
            out_of_stock.append(item)
        elif item.quantity_needed > 0:
            low_stock.append(item)
        else:
            complete.append(item)

    total_issues = len(out_of_stock) + len(low_stock)

    return render(
        request,
        "inventory/daily_report.html",
        {
            "formset": formset,
            "items": inventory_queryset,
            "email_recipients": email_recipients,
            "selected_recipient": selected_recipient,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "complete": complete,
            "latest_report": latest_report,
            "progress": progress_percentage,
            "reports": reports,
            "selected_date": selected_date,
            "total_issues": total_issues,
        },
    )


@login_required
def daily_report_detail(request, pk):
    """Staff members can open the detail page linked from the email."""
    if not _staff_access_allowed(request.user):
        messages.error(request, "Only staff members can view daily reports.")
        return redirect("inventory_list")

    report = get_object_or_404(DailyReport, pk=pk)
    snapshots = report.snapshots.all()

    out_of_stock = [s for s in snapshots if s.quantity_have == 0]
    low_stock = [
        s for s in snapshots
        if s.quantity_have > 0 and s.quantity_needed > 0
    ]
    complete = [s for s in snapshots if s.quantity_needed == 0]
    total_issues = len(out_of_stock) + len(low_stock)

    return render(
        request,
        "inventory/daily_report_detail.html",
        {
            "report": report,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "complete": complete,
            "total_issues": total_issues,
        },
    )


@manager_required
def api_docs(request):
    return render(request, "inventory/api_docs.html")


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]