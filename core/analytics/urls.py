from django.urls import path
from .views import dashboard_statistics,StatisticsAPIView

urlpatterns = [
    path("dashboard/cards-statistics/", dashboard_statistics, name="dashboard-statistics"),
    path("dashboard/chart-statistics/", StatisticsAPIView.as_view(), name="statistics"),
]