from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.throttling import AnonRateThrottle
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings as django_settings
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from .models import User
from kindergarten.models import Teacher, KindergartenAdmin
from kindergarten.permissions import IsSuperAdmin
from .serializers import (
    LoginSerializer, ParentRegistrationSerializer, TeacherRegistrationSerializer,
    AdminRegistrationSerializer, PinSerializer, PinLoginSerializer, EditProfileSerializer,
    UpdatePasswordSerializer, UserProfileSerializer, SuperAdminUserSerializer,
    SuperAdminEditUserSerializer, UserRoleChangeSerializer,
    AdminCreateParentSerializer, AdminCreateTeacherSerializer, AdminCreateAdminSerializer,
)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get user profile",
        operation_description="Returns the profile information of the authenticated user or a user based on the provided ID.",
        responses={200: UserProfileSerializer()}
    )
    def get(self, request, id=None):
        if id:
            # Fetch user by ID if provided
            user = get_object_or_404(User, id=id)
        else:
            # If no ID is provided, fetch based on authenticated user
            user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

class DeleteUserView(DestroyAPIView):
    permission_classes = [IsAdminUser]  # Only admins can delete users

    def delete(self, request, id):
        user = get_object_or_404(User, id=id)

        if user.role not in ["teacher", "parent"]:
            return Response({"message": "Only teachers and parents can be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        # If the user is a teacher, delete their associated record
        if user.role == "teacher":
            Teacher.objects.filter(user=user).delete()

        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)


class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=EditProfileSerializer)
    def put(self, request):
        user = request.user
        serializer = EditProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.auth.delete()  # Delete the user's token
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UpdatePasswordSerializer)
    def post(self, request):
        user = request.user
        serializer = UpdatePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            current_password = serializer.validated_data["current_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(current_password):
                return Response({"message": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny] 
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            fcm_token = request.data.get("fcm_token")  
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"message": "Account is deactivated. Contact your administrator."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            # Create or retrieve a token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminRegistrationView(APIView):
    @swagger_auto_schema(request_body=AdminRegistrationSerializer)
    def post(self, request):
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParentRegistrationView(APIView):
    
    @swagger_auto_schema(request_body=ParentRegistrationSerializer)
    
    def post(self, request):
        serializer = ParentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Parent registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherRegistrationView(APIView):
    @swagger_auto_schema(request_body=TeacherRegistrationSerializer)
    
    def post(self, request):
        serializer = TeacherRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Teacher registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPinView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PinSerializer)
    def post(self, request):
        serializer = PinSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            request.user.set_pin(serializer.validated_data["pin"])
            request.user.save()
            return Response({"message": "PIN set successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class PinLoginView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PinLoginSerializer)
    def post(self, request):
        serializer = PinLoginSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data["pin"]
            fcm_token = request.data.get("fcm_token")

            try:
                user = User.objects.get(pin__isnull=False)  # Find a user with a PIN set
            except ObjectDoesNotExist:
                return Response({"message": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_pin(pin):
                return Response({"message": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"message": "Account is deactivated. Contact your administrator."}, status=status.HTTP_403_FORBIDDEN)

            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            # Create or retrieve a token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Superadmin User Management ──────────────────────────────────────────────

class UserListView(APIView):
    """GET /users/list/ — list all users, filterable by role / is_active / kindergarten_id"""
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('role', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Filter by role (parent, teacher, admin, superadmin)'),
            openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Filter by active status'),
            openapi.Parameter('kindergarten_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Filter teachers/admins by kindergarten'),
        ],
        responses={200: SuperAdminUserSerializer(many=True)}
    )
    def get(self, request):
        qs = User.objects.all().order_by('-date_joined')

        role = request.GET.get('role')
        if role:
            qs = qs.filter(role=role)

        is_active = request.GET.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        kindergarten_id = request.GET.get('kindergarten_id')
        if kindergarten_id:
            teacher_user_ids = Teacher.objects.filter(
                kindergarten_id=kindergarten_id
            ).values_list('user_id', flat=True)
            admin_user_ids = KindergartenAdmin.objects.filter(
                kindergarten_id=kindergarten_id
            ).values_list('user_id', flat=True)
            qs = qs.filter(id__in=list(teacher_user_ids) + list(admin_user_ids))

        serializer = SuperAdminUserSerializer(qs, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """GET/PATCH /users/manage/<id>/ — view or edit any user (superadmin only)"""
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(responses={200: SuperAdminUserSerializer()})
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        return Response(SuperAdminUserSerializer(user).data)

    @swagger_auto_schema(request_body=SuperAdminEditUserSerializer, responses={200: SuperAdminUserSerializer()})
    def patch(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = SuperAdminEditUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(SuperAdminUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(APIView):
    """PATCH /users/manage/<id>/deactivate/ and /users/manage/<id>/activate/"""
    permission_classes = [IsSuperAdmin]

    def patch(self, request, id, action):
        user = get_object_or_404(User, id=id)
        if user.role == 'superadmin':
            return Response({"message": "Cannot deactivate a superadmin account."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'deactivate':
            user.is_active = False
            user.save()
            Token.objects.filter(user=user).delete()
            _audit(request.user, 'user_deactivated', 'User', user.id, {'email': user.email})
            return Response({"message": f"User {user.email} has been deactivated."})
        elif action == 'activate':
            user.is_active = True
            user.save()
            _audit(request.user, 'user_activated', 'User', user.id, {'email': user.email})
            return Response({"message": f"User {user.email} has been activated."})

        return Response({"message": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


class UserChangeRoleView(APIView):
    """PATCH /users/manage/<id>/change-role/"""
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(request_body=UserRoleChangeSerializer)
    def patch(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = UserRoleChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_role = user.role
        new_role = serializer.validated_data['role']

        if old_role == new_role:
            return Response({"message": "User already has this role."})

        if old_role == 'teacher':
            Teacher.objects.filter(user=user).delete()
        elif old_role == 'admin':
            KindergartenAdmin.objects.filter(user=user).delete()

        user.role = new_role
        user.save()
        _audit(request.user, 'role_changed', 'User', user.id, {'from': old_role, 'to': new_role, 'email': user.email})
        return Response({
            "message": f"Role changed from {old_role} to {new_role}.",
            "user": SuperAdminUserSerializer(user).data,
        })


# ── Admin-created users with auto-generated credentials ──────────────────────

def _audit(actor, action, target_model='', target_id=None, metadata=None):
    try:
        from audit.models import AuditLog
        AuditLog.objects.create(
            actor=actor,
            action=action,
            target_model=target_model,
            target_id=target_id,
            metadata=metadata or {},
        )
    except Exception:
        pass  # never break the request because of logging


def _send_credentials_email(email, password, role):
    subject = "Your Kindergarten App Account Credentials"
    message = (
        f"Hello,\n\n"
        f"Your {role} account has been created on the Kindergarten App.\n\n"
        f"Email: {email}\n"
        f"Password: {password}\n\n"
        f"Please log in and change your password as soon as possible.\n\n"
        f"Thank you."
    )
    try:
        send_mail(subject, message, django_settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception:
        pass  # best-effort


class AdminCreateParentView(APIView):
    """POST /users/admin/create-parent/ — superadmin or admin creates a parent, auto-emails credentials"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ('superadmin', 'admin'):
            return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminCreateParentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, password = serializer.save()
        _send_credentials_email(user.email, password, 'parent')
        _audit(request.user, 'user_created', 'User', user.id, {'email': user.email, 'role': 'parent'})
        return Response(
            {"message": "Parent account created. Credentials sent to their email.", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


class AdminCreateTeacherView(APIView):
    """POST /users/admin/create-teacher/ — superadmin or admin creates a teacher, auto-emails credentials"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ('superadmin', 'admin'):
            return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminCreateTeacherSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, password = serializer.save()
        _send_credentials_email(user.email, password, 'teacher')
        _audit(request.user, 'user_created', 'User', user.id, {'email': user.email, 'role': 'teacher'})
        return Response(
            {"message": "Teacher account created. Credentials sent to their email.", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


class AdminCreateAdminView(APIView):
    """POST /users/admin/create-admin/ — superadmin creates an admin, auto-emails credentials"""
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        serializer = AdminCreateAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, password = serializer.save()
        _send_credentials_email(user.email, password, 'admin')
        _audit(request.user, 'user_created', 'User', user.id, {'email': user.email, 'role': 'admin'})
        return Response(
            {"message": "Admin account created. Credentials sent to their email.", "user_id": user.id},
            status=status.HTTP_201_CREATED,
        )


class AdminResetCredentialsView(APIView):
    """POST /users/admin/reset-credentials/<id>/ — generate new password and email it to the user"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        from django.utils.crypto import get_random_string
        caller = request.user

        target = get_object_or_404(User, id=id)

        # Superadmin: can reset anyone except other superadmins
        if caller.role == 'superadmin':
            if target.role == 'superadmin' and target.id != caller.id:
                return Response({"message": "Cannot reset another superadmin's credentials."}, status=status.HTTP_403_FORBIDDEN)

        # Kindergarten admin: can only reset teachers in their own kindergarten
        elif caller.role == 'admin':
            if target.role != 'teacher':
                return Response({"message": "Admins can only reset teacher credentials."}, status=status.HTTP_403_FORBIDDEN)
            try:
                admin_kg = caller.kindergarten_admin.kindergarten
                teacher_kg = target.teacher_profile.kindergarten
                if admin_kg != teacher_kg:
                    return Response({"message": "Teacher does not belong to your kindergarten."}, status=status.HTTP_403_FORBIDDEN)
            except Exception:
                return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        new_password = get_random_string(10)
        target.set_password(new_password)
        target.save()
        _send_credentials_email(target.email, new_password, target.role)
        _audit(request.user, 'user_updated', 'User', target.id, {'action': 'credentials_reset', 'email': target.email})
        return Response({"message": f"New credentials sent to {target.email}."}, status=status.HTTP_200_OK)