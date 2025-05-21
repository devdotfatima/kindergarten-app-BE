from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NapViewSet

router = DefaultRouter()
router.register(r"naps", NapViewSet, basename="nap")

urlpatterns = [
    path("", include(router.urls)),
]