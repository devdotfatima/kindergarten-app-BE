from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,serializers
from django.shortcuts import get_object_or_404
from datetime import date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Nap
from .serializers import NapSerializer
from children.models import Children

class NapViewSet(ModelViewSet):
    queryset = Nap.objects.all()
    serializer_class = NapSerializer
    permission_classes = [IsAuthenticated]

    def has_kindergarten_access(self, user, child):
        """Check if the user has access to the child's kindergarten."""
        return (
            hasattr(user, "kindergarten_admin") and user.kindergarten_admin.kindergarten == child.kindergarten
        ) or (
            hasattr(user, "teacher_profile") and user.teacher_profile.kindergarten == child.kindergarten
        )

    def validate_permission(self, request, child):
        """Check if the user is authorized to manage this child's naps."""
        if not request.user.is_superuser and request.user.role not in ["admin", "teacher"]:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if request.user.role in ["admin", "teacher"] and not self.has_kindergarten_access(request.user, child):
            return Response({"error": "You do not have access to this kindergarten."}, status=status.HTTP_403_FORBIDDEN)

        return None



    @swagger_auto_schema(
        operation_description="Retrieve naps based on role and filters (child, date).",
        manual_parameters=[
            openapi.Parameter(
                "child_id", openapi.IN_QUERY,
                description="Filter naps by child ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "date", openapi.IN_QUERY,
                description="Filter naps by date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={200: NapSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Filter hygiene by child and date if requested."""
        return super().list(request, *args, **kwargs)


    def perform_create(self, serializer):
        """Ensure only authorized users can create naps."""
        child_id = self.request.data.get("child")
        child = get_object_or_404(Children, id=child_id)
        permission_error = self.validate_permission(self.request, child)

        if permission_error:
            raise serializers.ValidationError({"error": permission_error.data.get("error", "Permission denied.")})

        serializer.save()

    def get_queryset(self):
        """Filter naps based on role and query parameters (child & date)."""
        user = self.request.user

        if not user.is_authenticated:
            return Nap.objects.none()

        queryset = Nap.objects.all()

        if user.role == "admin" and hasattr(user, "kindergarten_admin"):
            queryset = queryset.filter(child__kindergarten=user.kindergarten_admin.kindergarten)

        elif user.role == "teacher" and hasattr(user, "teacher_profile"):
            teacher_classes = user.teacher_profile.teacher_classes.values_list("class_id", flat=True)
            queryset = queryset.filter(child__class_id__in=teacher_classes)

        elif user.role == "parent":
            queryset = queryset.filter(child__parent=user)

        child_id = self.request.query_params.get("child_id")
        nap_date = self.request.query_params.get("date", str(date.today()))  # Default to today

        if child_id:
            queryset = queryset.filter(child_id=child_id)

        if nap_date:
            queryset = queryset.filter(date=nap_date)

        return queryset