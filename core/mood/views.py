from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import date

from .models import ChildMood
from .serializers import ChildMoodSerializer
from .permissions import CanManageChildMood
from children.models import Children
from attendance.models import Attendance

class ChildMoodViewSet(ModelViewSet):
    queryset = ChildMood.objects.all()
    serializer_class = ChildMoodSerializer
    permission_classes = [IsAuthenticated, CanManageChildMood]

    def has_kindergarten_access(self, user, child):
        """Check if the user has access to the child's kindergarten."""
        return (
            hasattr(user, "kindergarten_admin") and user.kindergarten_admin.kindergarten == child.kindergarten
        ) or (
            hasattr(user, "teacher_profile") and user.teacher_profile.kindergarten == child.kindergarten
        )

    def validate_permission(self, request, child):
        """Common permission validation for kindergarten-based access."""
        if not request.user.is_superuser and request.user.role not in ["admin", "teacher"]:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role in ["admin", "teacher"] and not self.has_kindergarten_access(request.user, child):
            return Response({"error": "You do not have access to this kindergarten."}, status=status.HTTP_403_FORBIDDEN)
        
        return None    

    @swagger_auto_schema(
        operation_description="Retrieve child moods based on role and filters (child, date).",
        manual_parameters=[
            openapi.Parameter(
                "child_id", openapi.IN_QUERY,
                description="Filter moods by child ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "date", openapi.IN_QUERY,
                description="Filter moods by date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={200: ChildMoodSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Filter moods by child and date if requested."""
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Ensure only superadmins or kindergarten admins can create a mood entry."""
        child_id = self.request.data.get("child")
        child = get_object_or_404(Children, id=child_id)
        permission_error = self.validate_permission(self.request, child)

        if permission_error:
            error_message = permission_error.data.get("error", "Permission denied.")
            raise serializers.ValidationError({"error": error_message})

        # Prevent mood creation if the child has not checked in
        today = date.today()
        if not Attendance.objects.filter(child=child, date=today).exists():
            raise serializers.ValidationError({"error": "Cannot add mood. Child has not checked in today."})

        serializer.save()

    def get_queryset(self):
        """Filter moods based on role and query parameters (child & date)."""
        user = self.request.user
        if not user.is_authenticated:
            return ChildMood.objects.none()
        
        queryset = ChildMood.objects.all()

        if user.role == "admin" and hasattr(user, "kindergarten_admin"):
            queryset = queryset.filter(child__kindergarten=user.kindergarten_admin.kindergarten)

        elif user.role == "teacher" and hasattr(user, "teacher_profile"):
            teacher_classes = user.teacher_profile.teacher_classes.values_list("class_id", flat=True)
            queryset = queryset.filter(child__class_id__in=teacher_classes)

        elif user.role == "parent":
            queryset = queryset.filter(child__parent=user)

        child_id = self.request.query_params.get("child_id")
        mood_date = self.request.query_params.get("date")

        if child_id:
            queryset = queryset.filter(child_id=child_id)

        if mood_date:
            queryset = queryset.filter(date=mood_date)

        return queryset
