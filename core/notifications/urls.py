

from django.urls import path
from .views import (
    NotificationListAPIView,
    MarkNotificationReadAPIView,
    DeleteNotificationAPIView,
    SendNotificationAPIView,
)

urlpatterns = [
    path("notifications/", NotificationListAPIView.as_view(), name="list-notifications"),
    path("notifications/send/", SendNotificationAPIView.as_view(), name="send-notification"),
    path("notifications/<int:notification_id>/read/", MarkNotificationReadAPIView.as_view(), name="mark-notification-read"),
    path("notifications/<int:notification_id>/delete/", DeleteNotificationAPIView.as_view(), name="delete-notification"),
]