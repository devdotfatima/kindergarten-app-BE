from rest_framework import viewsets,permissions,status
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import KindergartenAdmin, Kindergarten,TeacherClass,KindergartenClass,Teacher
from .serializers import KindergartenSerializer,AttachAdminSerializer, DetachAdminSerializer,TeacherClassSerializer,ClassSerializer,TeacherSerializer
from .permissions import KindergartenPermission,IsSuperAdmin


User = get_user_model()

class KindergartenViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage kindergarten details.
    - Superadmins: Full access (CRUD).
    - Admins: Can only view & update their assigned kindergarten.
    - Others: No access.
    """

    serializer_class = KindergartenSerializer
    permission_classes = [permissions.IsAuthenticated, KindergartenPermission]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
          return Kindergarten.objects.none()

        if user.is_superuser or user.role == "superadmin":
            return Kindergarten.objects.all()

        if user.role == "admin":
            try:
                return Kindergarten.objects.filter(id=user.kindergarten_admin.kindergarten.id)
            except KindergartenAdmin.DoesNotExist:
                return Kindergarten.objects.none()

     
        return Kindergarten.objects.none()

    def destroy(self, request, *args, **kwargs):
        """Prevent admins from deleting kindergartens."""
        if request.user.role == "admin":
            return Response({"error": "You do not have permission to delete kindergartens."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class AttachAdminView(APIView):
    """
    Allows only superadmins to attach an admin to a kindergarten.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(request_body=AttachAdminSerializer)
    def post(self, request):
        serializer = AttachAdminSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            kindergarten_id = serializer.validated_data['kindergarten_id']

            # Check if the user exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Ensure the user is an admin
            if user.role != 'admin':
                return Response({"message": "Only users with the 'admin' role can be assigned."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the kindergarten exists
            try:
                kindergarten = Kindergarten.objects.get(id=kindergarten_id)
            except Kindergarten.DoesNotExist:
                return Response({"message": "Kindergarten not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the admin is already assigned to the kindergarten
            if KindergartenAdmin.objects.filter(user=user, kindergarten=kindergarten).exists():
                return Response({"message": "This admin is already assigned to the kindergarten."}, status=status.HTTP_400_BAD_REQUEST)

            # Attach the admin to the kindergarten
            KindergartenAdmin.objects.create(user=user, kindergarten=kindergarten)
            return Response({"message": "Admin attached successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class DetachAdminView(APIView):
    """
    Allows only superadmins to attach an admin to a kindergarten.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin] 
  
    @swagger_auto_schema(request_body=DetachAdminSerializer)

    def post(self, request):
        serializer = DetachAdminSerializer(data=request.data)
        if serializer.is_valid():
            # Detach the admin from the kindergarten
            user = User.objects.get(id=serializer.validated_data['user_id'])
            kindergarten = Kindergarten.objects.get(id=serializer.validated_data['kindergarten_id'])

            # Check if the admin exists for the given kindergarten
            try:
                kindergarten_admin = KindergartenAdmin.objects.get(user=user, kindergarten=kindergarten)
                kindergarten_admin.delete()
                return Response({"message": "Admin detached successfully."}, status=status.HTTP_204_NO_CONTENT)
            except KindergartenAdmin.DoesNotExist:
                return Response({"message": "Admin not found for the specified kindergarten."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ClassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        classes = KindergartenClass.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherViewSet(viewsets.ModelViewSet):
    """
    API endpoints to manage teachers.
    - Superadmins can view and delete all teachers.
    - Kindergarten Admins can only view and delete teachers from their own kindergarten.
    """
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return teachers based on user role:
        - Superadmin: All teachers
        - Kindergarten Admin: Only teachers in their kindergarten
        """
        user = self.request.user

        if user.is_superuser:
            return Teacher.objects.all()

        if hasattr(user, "kindergarten_admin"):
            return Teacher.objects.filter(kindergarten=user.kindergarten_admin.kindergarten)

        return Teacher.objects.none()  # No access for other users

    @swagger_auto_schema(
        summary="Get all teachers",
        responses={200: TeacherSerializer(many=True)}
    )
    @action(detail=False, methods=["GET"], url_path="all")
    def get_all_teachers(self, request):
        """
        Retrieve all teachers.
        - Superadmin: Gets all teachers.
        - Kindergarten Admin: Gets teachers only from their kindergarten.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        summary="Delete a teacher by ID",
        manual_parameters=[
            openapi.Parameter(
                name="teacher_id",
                in_=openapi.IN_PATH,
                description="ID of the teacher",
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={204: "Teacher deleted", 403: "Permission denied", 404: "Teacher not found"}
    )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a teacher and their associated user.
        - Superadmin can delete any teacher.
        - Kindergarten Admin can only delete teachers from their own kindergarten.
        """
        user = request.user
        teacher = self.get_object()

        # Superadmin can delete anyone
        if user.is_superuser or (hasattr(user, "kindergarten_admin") and teacher.kindergarten == user.kindergarten_admin.kindergarten):
            with transaction.atomic():  # Start a transaction
                user_to_delete = teacher.user  # Get associated user
                teacher.delete()  # Delete the teacher
                user_to_delete.delete()  # Delete the associated user
            return Response({"message": "Teacher and associated user deleted."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


class TeacherClassViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TeacherClassSerializer
    queryset = TeacherClass.objects.all()

    def get_queryset(self):
        """Filter teacher-class assignments based on user role"""
        user = self.request.user

        if not user.is_authenticated:
            return TeacherClass.objects.none()
      
        if user.role == "superadmin":
            return TeacherClass.objects.all()

        if user.role == "admin":
            try:
                admin = KindergartenAdmin.objects.get(user=user)
                return TeacherClass.objects.filter(class_id__kindergarten=admin.kindergarten)
            except KindergartenAdmin.DoesNotExist:
                return TeacherClass.objects.none()
        elif user.role=="teacher":
            teacher = Teacher.objects.get(user=user)
            return TeacherClass.objects.filter(teacher=teacher)

        return TeacherClass.objects.none()

    def create(self, request, *args, **kwargs):
        """Assign a teacher to a class"""
        user = request.user

        if user.role in ["superadmin", "admin"]:
            serializer = self.get_serializer(data=request.data)

           
            if serializer.is_valid():
             
                teacher = serializer.validated_data["teacher"]
                class_id = serializer.validated_data["class_id"]
             
                print("here",user.role == "superadmin" and teacher.kindergarten != class_id.kindergarten)
                if user.role == "superadmin" and teacher.kindergarten != class_id.kindergarten:
                    return Response(
                        {"error": "Teacher and class must belong to the same kindergarten."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                elif user.role == "admin":
                    try:
                        admin = KindergartenAdmin.objects.get(user=user)
                        if teacher.kindergarten != admin.kindergarten or class_id.kindergarten != admin.kindergarten:
                            return Response(
                                {"error": "Admins can only assign teachers within their kindergarten."},
                                status=status.HTTP_403_FORBIDDEN,
                            )
                    except KindergartenAdmin.DoesNotExist:
                        return Response(
                            {"error": "You are not assigned as an admin for any kindergarten."},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                serializer.save()


            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "You do not have permission to assign teachers to classes."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        """Update a teacher-class assignment"""
        user = request.user
        instance = self.get_object()

        if user.role == "superadmin":
            return super().update(request, *args, **kwargs)

        elif user.role == "admin":
            try:
                admin = KindergartenAdmin.objects.get(user=user)
                if instance.teacher.kindergarten != admin.kindergarten:
                    return Response(
                        {"error": "Admins can only update assignments within their kindergarten."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except KindergartenAdmin.DoesNotExist:
                return Response(
                    {"error": "You are not assigned as an admin for any kindergarten."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return super().update(request, *args, **kwargs)

        return Response({"error": "You do not have permission to update this assignment."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """Delete a teacher-class assignment"""
        user = request.user
        instance = self.get_object()

        if user.role == "superadmin":
            return super().destroy(request, *args, **kwargs)

        elif user.role == "admin":
            try:
                admin = KindergartenAdmin.objects.get(user=user)
                if instance.teacher.kindergarten != admin.kindergarten:
                    return Response(
                        {"error": "Admins can only delete assignments within their kindergarten."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except KindergartenAdmin.DoesNotExist:
                return Response(
                    {"error": "You are not assigned as an admin for any kindergarten."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return super().destroy(request, *args, **kwargs)

        return Response({"error": "You do not have permission to delete this assignment."}, status=status.HTTP_403_FORBIDDEN)