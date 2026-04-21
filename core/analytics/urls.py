from django.urls import path
from .views import dashboard_statistics, StatisticsAPIView, TeacherActivityView, StudentProgressView, AttendanceReportView

urlpatterns = [
    path("dashboard/cards-statistics/", dashboard_statistics, name="dashboard-statistics"),
    path("dashboard/chart-statistics/", StatisticsAPIView.as_view(), name="statistics"),
    path("teacher-activity/", TeacherActivityView.as_view(), name="teacher-activity"),
    path("student-progress/<int:child_id>/", StudentProgressView.as_view(), name="student-progress"),
    path("attendance-report/", AttendanceReportView.as_view(), name="attendance-report"),
]