import csv
import json
from datetime import date
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import User
from kindergarten.permissions import IsSuperAdmin


class FullDataExportView(APIView):
    """GET /users/export/full/ — Superadmin only. Downloads all data as JSON."""
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        from kindergarten.models import Kindergarten, Teacher, KindergartenClass
        from posts.models import Post
        from children.models import Child

        data = {
            "exported_at": date.today().isoformat(),
            "users": list(User.objects.values(
                "id", "email", "username", "first_name", "last_name",
                "role", "is_active", "phone_number", "date_joined"
            )),
            "kindergartens": list(Kindergarten.objects.values()),
            "teachers": list(Teacher.objects.values("id", "user_id", "kindergarten_id")),
            "classes": list(KindergartenClass.objects.values()),
            "children": list(Child.objects.values()),
            "posts": list(Post.objects.values(
                "id", "title", "description", "kindergarten_id", "author_id", "created_at"
            )),
        }

        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="full_export_{date.today()}.json"'
        return response


class KindergartenDataExportView(APIView):
    """GET /users/export/my-kindergarten/ — Admin only. Downloads scoped kindergarten data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'admin' and not (user.is_superuser or user.role == 'superadmin'):
            from rest_framework.response import Response
            from rest_framework import status
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        try:
            kg = user.kindergarten_admin.kindergarten
        except Exception:
            from rest_framework.response import Response
            from rest_framework import status
            return Response({"detail": "You are not associated with a kindergarten."}, status=status.HTTP_400_BAD_REQUEST)

        from kindergarten.models import Teacher, KindergartenClass
        from posts.models import Post
        from children.models import Child

        teacher_user_ids = Teacher.objects.filter(kindergarten=kg).values_list("user_id", flat=True)
        child_parent_ids = Child.objects.filter(kindergarten=kg).values_list("parent_id", flat=True)
        parent_user_ids = User.objects.filter(id__in=child_parent_ids, role="parent").values_list("id", flat=True)

        data = {
            "exported_at": date.today().isoformat(),
            "kindergarten": {
                "id": kg.id,
                "name": kg.name,
            },
            "teachers": list(User.objects.filter(id__in=teacher_user_ids).values(
                "id", "email", "first_name", "last_name", "phone_number", "is_active"
            )),
            "classes": list(KindergartenClass.objects.filter(kindergarten=kg).values()),
            "children": list(Child.objects.filter(kindergarten=kg).values()),
            "parents": list(User.objects.filter(id__in=parent_user_ids).values(
                "id", "email", "first_name", "last_name", "phone_number", "is_active"
            )),
            "posts": list(Post.objects.filter(kindergarten=kg).values(
                "id", "title", "description", "author_id", "created_at"
            )),
        }

        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="kindergarten_export_{date.today()}.json"'
        return response


class AccessLogsExportView(APIView):
    """GET /users/export/access-logs/ — Superadmin: all logs. Admin: their own logs. Returns CSV."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in ('admin', 'superadmin') and not user.is_superuser:
            from rest_framework.response import Response
            from rest_framework import status
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        from audit.models import AuditLog
        qs = AuditLog.objects.select_related("actor").order_by("-timestamp")
        if user.role == 'admin':
            qs = qs.filter(actor=user)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="access_logs_{date.today()}.csv"'

        writer = csv.writer(response)
        writer.writerow(["ID", "Actor Email", "Action", "Target Model", "Target ID", "Metadata", "Timestamp"])
        for log in qs:
            writer.writerow([
                log.id,
                log.actor.email if log.actor else "",
                log.action,
                log.target_model,
                log.target_id,
                json.dumps(log.metadata) if log.metadata else "",
                log.timestamp.isoformat() if log.timestamp else "",
            ])

        return response
