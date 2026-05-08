from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from kindergarten.permissions import IsSuperAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AccessLogView(APIView):
    """GET /admin/access-logs/
    Superadmin: all logs.
    Admin: only logs where actor=self.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('action', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Filter by action type'),
            openapi.Parameter('actor_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Filter by actor user ID'),
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Start date (YYYY-MM-DD)'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='End date (YYYY-MM-DD)'),
        ],
        responses={200: AuditLogSerializer(many=True)},
    )
    def get(self, request):
        user = request.user
        if user.role not in ('admin', 'superadmin') and not user.is_superuser:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        qs = AuditLog.objects.all()

        # Admin can only see their own audit logs
        if user.role == 'admin':
            qs = qs.filter(actor=user)

        action = request.GET.get('action')
        if action:
            qs = qs.filter(action=action)

        actor_id = request.GET.get('actor_id')
        if actor_id:
            qs = qs.filter(actor_id=actor_id)

        start_date = request.GET.get('start_date')
        if start_date:
            qs = qs.filter(timestamp__date__gte=start_date)

        end_date = request.GET.get('end_date')
        if end_date:
            qs = qs.filter(timestamp__date__lte=end_date)

        serializer = AuditLogSerializer(qs[:200], many=True)
        return Response(serializer.data)
