from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from kindergarten.permissions import IsSuperAdmin
from .models import SystemSetting
from .serializers import SystemSettingSerializer


class SystemSettingListView(APIView):
    """GET /system/settings/ — list all system settings (superadmin only)"""
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(responses={200: SystemSettingSerializer(many=True)})
    def get(self, request):
        settings = SystemSetting.objects.all().order_by('key')
        return Response(SystemSettingSerializer(settings, many=True).data)


class SystemSettingDetailView(APIView):
    """PATCH /system/settings/<key>/ — update a system setting value (superadmin only)"""
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(request_body=SystemSettingSerializer, responses={200: SystemSettingSerializer()})
    def patch(self, request, key):
        setting = get_object_or_404(SystemSetting, key=key)
        serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
