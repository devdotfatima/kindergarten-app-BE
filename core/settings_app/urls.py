from django.urls import path
from .views import SystemSettingListView, SystemSettingDetailView

urlpatterns = [
    path('settings/', SystemSettingListView.as_view(), name='system-settings-list'),
    path('settings/<str:key>/', SystemSettingDetailView.as_view(), name='system-settings-detail'),
]
