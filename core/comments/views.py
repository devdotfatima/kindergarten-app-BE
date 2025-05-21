
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import CommentSerializer
from .models import Comment


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve hygiene based on role and filters (child, date).",
        manual_parameters=[
            openapi.Parameter(
                "post_id", openapi.IN_QUERY,
                description="Filter comments by post ID",
                type=openapi.TYPE_INTEGER
            ),
         
        ],
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Filter hygiene by child and date if requested."""
        return super().list(request, *args, **kwargs)
    def get_queryset(self):
        """
        Retrieve a list of comments.

        Query Parameters:
        - `post_id` (optional): Filter comments by a specific post.

        Example:
        ```
        GET /comments/?post_id=5
        ```
        Returns all comments related to the post with `id=5`.
        """
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=["POST"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        """
        Toggle like status for a comment.
        """
        user = request.user
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if user in comment.likes.all():
            comment.likes.remove(user)
            return Response({"message": "Comment unliked."}, status=status.HTTP_200_OK)
        else:
            comment.likes.add(user)
            return Response({"message": "Comment liked."}, status=status.HTTP_200_OK)