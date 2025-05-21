from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.throttling import AnonRateThrottle
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from .models import User
from kindergarten.models  import Teacher
from .serializers import LoginSerializer,ParentRegistrationSerializer, TeacherRegistrationSerializer,AdminRegistrationSerializer,PinSerializer,PinLoginSerializer,EditProfileSerializer,UpdatePasswordSerializer



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


            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            # Create or retrieve a token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)