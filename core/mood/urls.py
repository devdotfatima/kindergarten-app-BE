from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChildMoodViewSet

router = DefaultRouter()
router.register(r"moods", ChildMoodViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
