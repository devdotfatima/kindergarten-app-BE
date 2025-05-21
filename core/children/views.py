


from rest_framework import viewsets, status,permissions,views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Children
from kindergarten.models import KindergartenClass
from .serializers import ChildrenSerializer,KindergartenClassSerializer



class TeacherClassesView(views.APIView):
    """
    Get all classes assigned to the authenticated teacher.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, "teacher_profile"):
            return Response({"error": "Only teachers can access this"}, status=403)

        teacher = request.user.teacher_profile
        classes = KindergartenClass.objects.filter(kindergarten=teacher.kindergarten, kindergarten_class__teacher=teacher).distinct()
        serializer = KindergartenClassSerializer(classes, many=True)
        return Response(serializer.data)

class ClassChildrenView(views.APIView):
    """
    Get all children in a specific class.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        try:
            children = Children.objects.filter(class_id=class_id)
            serializer = ChildrenSerializer(children, many=True)
            return Response(serializer.data)
        except KindergartenClass.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)



class ChildrenViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing children.

    - `GET /children/` → List all children
    - `POST /children/` → Register a new child
    - `GET /children/{id}/` → Retrieve a child
    - `PUT /children/{id}/` → Update child details
    - `DELETE /children/{id}/` → Delete a child
    """
    # queryset = Children.objects.all()
    queryset = Children.objects.select_related("kindergarten", "class_id")
    serializer_class = ChildrenSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """Custom delete response message."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Child deleted successfully"}, status=status.HTTP_204_NO_CONTENT)