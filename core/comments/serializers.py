from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name","last_name", "profile_picture"]

class CommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)  # Populate user with name and profile_picture

    class Meta:
        model = Comment
        fields = ["id", "user", "post", "content", "created_at", "likes_count"]
        read_only_fields = ["user", "created_at"]
    
    def get_likes_count(self, obj):
        return obj.likes.count()