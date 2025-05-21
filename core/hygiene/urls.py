from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HygieneViewSet

router = DefaultRouter()
router.register(r"hygiene", HygieneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]