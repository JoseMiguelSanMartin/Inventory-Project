from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("items", views.InventoryItemViewSet)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path("create/", views.inventory_create, name="inventory_create"),
    path("<int:pk>/edit/", views.inventory_update, name="inventory_update"),
    path("<int:pk>/delete/", views.inventory_delete, name="inventory_delete"),
    path("api/docs/", views.api_docs, name="api_docs"),
    path("api/", include(router.urls)),
    path("daily-report/submit/", views.submit_daily_report, name="submit_daily_report"),
    path("daily-report/", views.daily_report, name="daily_report"),
    path("daily-report/<int:pk>/", views.daily_report_detail, name="daily_report_detail"),
]