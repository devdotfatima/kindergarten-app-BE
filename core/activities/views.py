from django.shortcuts import get_object_or_404
from datetime import date
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Activity
from children.models import Children
from .serializers import ActivitySerializer
from .permissions import ActivityPermission
# Create your views here.


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all().order_by('-time')
    serializer_class = ActivitySerializer
    permission_classes = [ActivityPermission]

    def get_queryset(self):
        """Filter activities based on role and query parameters (child & date)."""
        user = self.request.user

        if not user.is_authenticated:
            return Activity.objects.none()

        queryset = Activity.objects.all()

        if user.role == "superadmin":
            queryset = Activity.objects.all()

        elif user.role == "admin" and hasattr(user, "kindergarten_admin"):
            queryset = queryset.filter(class_id__kindergarten=user.kindergarten_admin.kindergarten)

        elif user.role == "teacher" and hasattr(user, "teacher_profile"):
            teacher_classes = user.teacher_profile.teacher_classes.values_list("class_id", flat=True)
            queryset = queryset.filter(class_id__in=teacher_classes)

        elif user.role == "parent":
            queryset = queryset.filter(children__parent=user).distinct()  # Parents can only see activities of their children

        # Filter by child_id if provided
        child_id = self.request.query_params.get("child_id")
        activity_date = self.request.query_params.get("date")  # Default to today

        if child_id:
            queryset = queryset.filter(children__id=child_id)

        if activity_date:
            queryset = queryset.filter(time__date=activity_date)

        return queryset
            
    
    def perform_create(self, serializer):
        user = self.request.user

        class_id = serializer.validated_data["class_id"]

        if user.role == "admin":
            # Ensure class belongs to the admin's kindergarten
            if class_id.kindergarten != user.kindergarten_admin.kindergarten:
                raise PermissionDenied("You do not have permission to create an activity for this class.")

        elif user.role == "teacher":
            # Ensure class is one of the teacher's assigned classes
            allowed_classes = user.teacher_profile.teacher_classes.values_list("class_id", flat=True)
            if class_id.id not in allowed_classes:
                raise PermissionDenied("You do not have permission to create an activity for this class.")

        serializer.save()

    @swagger_auto_schema(
        operation_description="Retrieve activities based on role and filters (child, date).",
        manual_parameters=[
            openapi.Parameter(
                "child_id", openapi.IN_QUERY,
                description="Filter activities by child ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "date", openapi.IN_QUERY,
                description="Filter activities by date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={200: ActivitySerializer(many=True)}
    )

    def list(self, request, *args, **kwargs):
        """Filter activities by child and date if requested."""
        return super().list(request, *args, **kwargs)


    @action(detail=False, methods=['get'])
    def child_activities(self, request):
        child_id = request.query_params.get('child_id')
        date_filter = request.query_params.get('date', date.today())
        child = get_object_or_404(Children, id=child_id)
        activities = child.activities.filter(time__date=date_filter)
        return Response(ActivitySerializer(activities, many=True).data)
