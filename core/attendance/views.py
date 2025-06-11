from rest_framework import viewsets, status
from rest_framework.decorators import action
from datetime import date
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from children.models import Children
from .serializers import AttendanceSerializer
from .permissions import CanManageAttendance

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Attendance:
    - Superadmins & Admins have full access.
    - Teachers & Parents have restricted access based on their roles.
    """
    queryset = Attendance.objects.select_related("child").all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, CanManageAttendance]

    def has_kindergarten_access(self, user, child):
        """Check if the user has access to the child's kindergarten."""
        return (
            hasattr(user, "kindergarten_admin") and user.kindergarten_admin.kindergarten == child.kindergarten
        ) or (
            hasattr(user, "teacher_profile") and user.teacher_profile.kindergarten == child.kindergarten
        )

    def validate_permission(self, request, child):
        user = request.user

        if user.role == "superadmin":
            return None

        if user.role == "parent":
            if child.parent == user:
                return None
            return Response({"error": "You can only access your own child's attendance."}, status=status.HTTP_403_FORBIDDEN)

        if user.role in ["admin", "teacher"] and self.has_kindergarten_access(user, child):
            return None

        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


    @action(detail=False, methods=["get"], url_path="by-child/(?P<child_id>[^/.]+)/by-date")
    def get_attendance_by_child_and_date(self, request, child_id=None):
        """Fetch attendance for a child on a specific date (default: today)."""
        child = get_object_or_404(Children, id=child_id)
        permission_error = self.validate_permission(request, child)
        if permission_error:
            return permission_error
        
        query_date = request.query_params.get("date", str(date.today()))
        attendance_record = Attendance.objects.filter(child=child, date=query_date).first()
        
        if not attendance_record:
            return Response({"message": "No attendance record found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(AttendanceSerializer(attendance_record).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="by-child/(?P<child_id>[^/.]+)")
    def get_attendance_by_child(self, request, child_id=None):
        """Fetch attendance records for a specific child."""
        child = get_object_or_404(Children, id=child_id)
        permission_error = self.validate_permission(request, child)
        if permission_error:
            return permission_error
        
        attendance_records = child.attendances.all().order_by("-date")
        return Response(AttendanceSerializer(attendance_records, many=True).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Ensure only superadmins or kindergarten admins can create an attendance record."""
        child_id = request.data.get("child")
        child = get_object_or_404(Children, id=child_id)
        permission_error = self.validate_permission(request, child)
        if permission_error:
            return permission_error
        if request.user.role == "parent":
          return Response({"error": "Parents cannot create attendance records."}, status=status.HTTP_403_FORBIDDEN)

        if Attendance.objects.filter(child_id=child_id, date=request.data.get("date",str(date.today()))).exists():
            return Response({"error": "Attendance record already exists for this date."}, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)