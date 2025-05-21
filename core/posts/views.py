from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, serializers, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Post
from kindergarten.models import Kindergarten,KindergartenClass
from .serializers import PostSerializer
from .permissions import CanManagePosts

class PostViewSet(ModelViewSet):
    """
    Manage posts with filtering and role-based permissions.
    """
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["class_id"]  
    search_fields = ["title", "description"]  
    permission_classes = [permissions.IsAuthenticated, CanManagePosts]

    def get_queryset(self):
        """
        Return posts based on the user's role:
        - Superadmin: All posts
        - Admin: Posts in their kindergarten
        - Teacher: Posts in their assigned class
        - Parent: Posts related to their child's class and kindergarten
        """
        user = self.request.user

        if user.is_superuser:
            return Post.objects.all()

        if hasattr(user, "kindergarten_admin"):
            return Post.objects.filter(kindergarten=user.kindergarten_admin.kindergarten)

        if hasattr(user, "teacher_profile"):
            return Post.objects.filter(class_id__in=user.teacher_profile.teacher_classes.values_list("id", flat=True))

        if hasattr(user, "parent"):
            child_classes = user.parent.children.values_list("class_id", flat=True)
            child_kindergartens = user.parent.children.values_list("kindergarten_id", flat=True)
            return Post.objects.filter(class_id__in=child_classes) | Post.objects.filter(kindergarten_id__in=child_kindergartens)

        return Post.objects.none()

    @swagger_auto_schema(
        summary="Get posts by kindergarten ID",
        manual_parameters=[
            openapi.Parameter(
                name="kindergarten_id",
                in_=openapi.IN_PATH,
                description="ID of the kindergarten",
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: PostSerializer(many=True)}
    )
    @action(detail=False, methods=["GET"], url_path="by-kindergarten/(?P<kindergarten_id>\\d+)")
    def get_posts_by_kindergarten(self, request, kindergarten_id=None):
        """
        Retrieve posts belonging to a specific kindergarten.

        **Access Control:**
        - Superadmins: Can access all kindergartens.
        - Admins: Can access only their own kindergarten's posts.
        - Teachers: Can access posts if they teach in the kindergarten.
        - Parents: Can access posts if their child belongs to the kindergarten.
        """
        user = request.user

        if user.is_superuser:
            posts = Post.objects.filter(kindergarten_id=kindergarten_id)
        elif hasattr(user, "kindergarten_admin") and user.kindergarten_admin.kindergarten.id == int(kindergarten_id):
            posts = Post.objects.filter(kindergarten_id=kindergarten_id,class_id=None)
        elif hasattr(user, "teacher_profile") and user.teacher_profile.kindergarten.id == int(kindergarten_id):
            posts = Post.objects.filter(kindergarten_id=kindergarten_id)
        elif hasattr(user, "parent") and user.parent.children.filter(kindergarten_id=kindergarten_id).exists():
            posts = Post.objects.filter(kindergarten_id=kindergarten_id)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        summary="Get posts by class ID",
        manual_parameters=[
            openapi.Parameter(
                name="class_id",
                in_=openapi.IN_PATH,
                description="ID of the class",
                required=True,
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: PostSerializer(many=True)}
    )
    @action(detail=False, methods=["GET"], url_path="by-class/(?P<class_id>\\d+)")
    def get_posts_by_class(self, request, class_id=None):
        """
        Retrieve posts for a specific class.

        **Access Control:**
        - Superadmins: Can access all classes.
        - Kindergarten Admins: Can access posts if the class belongs to their kindergarten.
        - Teachers: Can access posts if assigned to the class.
        - Parents: Can access posts if their child is in the class.
        """
        user = request.user
        print(Post.objects.filter(class_id=class_id, kindergarten=user.kindergarten_admin.kindergarten).exists())
        if user.is_superuser:
            posts = Post.objects.filter(class_id=class_id)
        elif hasattr(user, "kindergarten_admin") and Post.objects.filter(class_id=class_id, kindergarten=user.kindergarten_admin.kindergarten).exists():
            posts = Post.objects.filter(class_id=class_id)
        elif hasattr(user, "teacher_profile") and int(class_id) in user.teacher_profile.teacher_classes.values_list("id", flat=True):
            posts = Post.objects.filter(class_id=class_id)
        elif hasattr(user, "parent") and user.parent.children.filter(class_id=class_id).exists():
            posts = Post.objects.filter(class_id=class_id)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
    summary="Like/Unlike a post",
    responses={200: "Success", 400: "Invalid request", 404: "Post not found"},
    )
    @action(detail=True, methods=["POST"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        """
        Toggle like status for a post.
        
        - If the user has already liked it, they will unlike it.
        - If the user has not liked it, they will like it.
        """
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Post unliked."}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            return Response({"message": "Post liked."}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Ensure only authorized users can create posts and enforce the correct rules.
        """
        user = self.request.user
        kindergarten_id = self.request.data.get("kindergarten")
        class_id = self.request.data.get("class_id")

        # Ensure kindergarten exists
        try:
            kindergarten = Kindergarten.objects.get(id=kindergarten_id)
        except Kindergarten.DoesNotExist:
            raise serializers.ValidationError({"kindergarten": "Invalid kindergarten ID."})
        kindergarten_class = None
        if class_id:
            try:
                kindergarten_class = KindergartenClass.objects.get(id=class_id)
            except KindergartenClass.DoesNotExist:
                raise serializers.ValidationError({"class_id": "Invalid class ID."})
        # Superadmin can create posts freely
        if user.is_superuser:
            serializer.save(kindergarten=kindergarten,class_id=kindergarten_class)
            return

        # Kindergarten Admin must be associated with the kindergarten they are posting for
        if hasattr(user, "kindergarten_admin"):
            if user.kindergarten_admin.kindergarten.id != kindergarten.id:
                raise serializers.ValidationError({"error": "You can only post in your own kindergarten."})
            
            # Kindergarten Admin can create posts for all classes (without class_id) or for a specific class
            serializer.save(kindergarten=kindergarten, class_id=kindergarten_class)
            return

        # Teachers can only post in their assigned class
        if hasattr(user, "teacher_profile"):
            teacher_class = user.teacher_profile.teacher_classes
            assigned_classes = teacher_class.values_list("class_id", flat=True) 

            if class_id is None:
                raise serializers.ValidationError({"class_id": "Teachers must specify a class when creating a post."})

            if int(class_id) not in assigned_classes:
              raise serializers.ValidationError({"error": "You can only post in your assigned class(es)."})

            serializer.save(kindergarten=kindergarten, class_id_id=class_id)
            return

        # If none of the above, user is not allowed to create a post
        raise serializers.ValidationError({"error": "You do not have permission to create a post."})

