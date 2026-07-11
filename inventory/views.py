import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import ExpressionWrapper, F, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .forms import InventoryItemForm, InventoryQuantityFormSet, SignUpForm
from .models import DailyReport, DailyReportSnapshot, InventoryItem
from .serializers import InventoryItemSerializer


logger = logging.getLogger(__name__)


def _is_manager(user):
    return (
        user.is_authenticated
        and user.is_active
        and (
            user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )
    )


def _staff_access_allowed(user):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_staff or user.is_superuser)
    )


manager_required = user_passes_test(_is_manager, login_url="login")


def build_report_url(report):
    report_path = reverse("daily_report_detail", args=[report.pk])
    return f"{settings.SITE_URL.rstrip('/')}{report_path}"


def send_daily_report_email(request, report, recipient_email):
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

    submitter_name = (
        report.submitted_by.get_full_name()
        or report.submitted_by.username
    )

    context = {
        "report": report,
        "submitter_name": submitter_name,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "complete": complete,
        "report_url": build_report_url(report),
    }

    text_body = render_to_string(
        "inventory/emails/daily_report.txt",
        context,
    )
    html_body = render_to_string(
        "inventory/emails/daily_report.html",
        context,
    )

    reply_to = (
        [request.user.email]
        if request.user.email
        else None
    )

    email = EmailMultiAlternatives(
        subject=f"Daily Inventory Report - {report.submitted_at:%B %d, %Y}",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
        reply_to=reply_to,
    )
    email.attach_alternative(html_body, "text/html")
    return email.send(fail_silently=False)


def update_email_success(report):
    report.email_sent = True
    report.email_sent_at = timezone.now()
    report.email_error = ""
    report.save(
        update_fields=[
            "email_sent",
            "email_sent_at",
            "email_error",
        ]
    )


def update_email_failure(report, error):
    report.email_sent = False
    report.email_error = str(error)
    report.save(
        update_fields=[
            "email_sent",
            "email_error",
        ]
    )


def home(request):
    if request.user.is_authenticated:
        return redirect("inventory_list")
    return render(request, "inventory/home.html")


@manager_required
def signup(request):
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        new_user = form.save()
        messages.success(
            request,
            f'User "{new_user.username}" was created successfully.',
        )
        return redirect("inventory_list")

    return render(
        request,
        "registration/signup.html",
        {"form": form},
    )


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

    context = {
        "items": items,
        "query": query,
        "status": status,
        "complete_count": sum(
            1 for item in items if item.quantity_needed == 0
        ),
        "missing_count": sum(
            1 for item in items if item.quantity_needed > 0
        ),
        "total_needed": sum(
            item.quantity_needed for item in items
        ),
    }

    return render(
        request,
        "inventory/inventory_list.html",
        context,
    )


@login_required
def inventory_create(request):
    if not _staff_access_allowed(request.user):
        messages.error(
            request,
            "Only staff members can add inventory items.",
        )
        return redirect("inventory_list")

    form = InventoryItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item added successfully.")
        return redirect("inventory_list")

    return render(
        request,
        "inventory/inventory_form.html",
        {"form": form},
    )


@manager_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(
        request.POST or None,
        instance=item,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item updated successfully.")
        return redirect("inventory_list")

    return render(
        request,
        "inventory/inventory_form.html",
        {
            "form": form,
            "item": item,
        },
    )


@manager_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == "POST":
        item_name = item.item_name
        item.delete()
        messages.success(
            request,
            f'"{item_name}" was deleted.',
        )
        return redirect("inventory_list")

    return render(
        request,
        "inventory/inventory_confirm_delete.html",
        {"item": item},
    )


@login_required
def submit_daily_report(request):
    if not _staff_access_allowed(request.user):
        messages.error(
            request,
            "Only staff members can submit daily reports.",
        )
        return redirect("inventory_list")

    messages.info(
        request,
        "Choose an email recipient before submitting the report.",
    )
    return redirect("daily_report")


@login_required
def daily_report(request):
    if not _staff_access_allowed(request.user):
        messages.error(
            request,
            "Only staff members can submit daily reports.",
        )
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
        selected_recipient = request.POST.get(
            "recipient_email",
            "",
        ).strip()

        recipient_is_valid = True

        try:
            validate_email(selected_recipient)
        except ValidationError:
            recipient_is_valid = False
            messages.error(
                request,
                "Please select a valid email recipient.",
            )

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
            with transaction.atomic():
                formset.save()

                report = DailyReport.objects.create(
                    submitted_by=request.user,
                    recipient_email=selected_recipient,
                )

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
                logger.exception(
                    "Failed to email daily report %s",
                    report.pk,
                )
                update_email_failure(report, error)
                messages.warning(
                    request,
                    (
                        "The report was saved, but the email could not "
                        "be sent. A manager can retry it from the report."
                    ),
                )
            else:
                update_email_success(report)
                messages.success(
                    request,
                    (
                        "Daily report submitted and emailed to "
                        f"{selected_recipient}."
                    ),
                )

            return redirect(
                "daily_report_detail",
                pk=report.pk,
            )

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
        reports = reports.filter(
            submitted_at__date=selected_date
        )

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

    context = {
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
        "total_issues": len(out_of_stock) + len(low_stock),
    }

    return render(
        request,
        "inventory/daily_report.html",
        context,
    )


@login_required
def daily_report_detail(request, pk):
    if not _staff_access_allowed(request.user):
        messages.error(
            request,
            "Only staff members can view daily reports.",
        )
        return redirect("inventory_list")

    report = get_object_or_404(DailyReport, pk=pk)
    snapshots = report.snapshots.all()

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

    return render(
        request,
        "inventory/daily_report_detail.html",
        {
            "report": report,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "complete": complete,
            "total_issues": len(out_of_stock) + len(low_stock),
            "can_resend": _is_manager(request.user),
        },
    )


@manager_required
def resend_daily_report_email(request, pk):
    report = get_object_or_404(DailyReport, pk=pk)

    if request.method != "POST":
        return redirect(
            "daily_report_detail",
            pk=report.pk,
        )

    if not report.recipient_email:
        messages.error(
            request,
            "This report has no saved recipient email address.",
        )
        return redirect(
            "daily_report_detail",
            pk=report.pk,
        )

    try:
        send_daily_report_email(
            request=request,
            report=report,
            recipient_email=report.recipient_email,
        )
    except Exception as error:
        logger.exception(
            "Failed to resend daily report %s",
            report.pk,
        )
        update_email_failure(report, error)
        messages.error(
            request,
            "The report email could not be resent.",
        )
    else:
        update_email_success(report)
        messages.success(
            request,
            f"Report resent to {report.recipient_email}.",
        )

    return redirect(
        "daily_report_detail",
        pk=report.pk,
    )


@manager_required
def api_docs(request):
    return render(request, "inventory/api_docs.html")


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]
