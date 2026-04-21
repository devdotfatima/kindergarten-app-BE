from django.urls import path
from .views import AccessLogView

urlpatterns = [
    path('access-logs/', AccessLogView.as_view(), name='access-logs'),
]
