import firebase_admin
from firebase_admin import credentials, messaging
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from auth_app.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


if not firebase_admin._apps:
    cred = credentials.Certificate("karimcrafts-firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_summary="Get notifications",
        operation_description="Retrieve a list of notifications for the authenticated user.",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Mark notification as read",
        operation_description="Mark a specific notification as read.",
        responses={200: openapi.Response("Notification marked as read"), 404: openapi.Response("Notification not found")}
    )

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"success": "Notification marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)


class DeleteNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_summary="Delete notification",
        operation_description="Delete a specific notification.",
        responses={200: openapi.Response("Notification deleted"), 404: openapi.Response("Notification not found")}
    )

    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return Response({"success": "Notification deleted"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)


class SendNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Send notification",
        operation_description="Send a notification to all users with a specified role.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "message", "role"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Title of the notification"),
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Message content"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, description="Role of users to send notification to"),
            }
        ),
        responses={
            200: openapi.Response("Success"),
            400: openapi.Response("Title and message are required"),
            403: openapi.Response("Access Denied"),
            404: openapi.Response("No users found with this role")
        }
    )

    def post(self, request):
        if request.user.role != "superadmin":
            return Response({"error": "Access Denied"}, status=403)

        title = request.data.get("title")
        message = request.data.get("message")
        role = request.data.get("role")

        if not title or not message:
            return Response({"error": "Title and message are required"}, status=400)

        users = User.objects.filter(role=role).exclude(fcm_token=None)

        for user in users:
            Notification.objects.create(user=user, title=title, message=message)

        tokens = [user.fcm_token for user in users]
        if not tokens:
            return Response({"error": "No users found with this role"}, status=404)
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=message),
            tokens=tokens,
        )

        response = messaging.send_multicast(message)

        return Response({"success": f"Sent to {response.success_count} devices"})