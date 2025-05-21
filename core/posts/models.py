from django.db import models
from django.contrib.auth import get_user_model
from kindergarten.models import Teacher, Kindergarten, KindergartenClass

User = get_user_model()

class Post(models.Model):
    kindergarten = models.ForeignKey(Kindergarten, on_delete=models.CASCADE, related_name="kindergarten_posts")
    class_id = models.ForeignKey(KindergartenClass, on_delete=models.SET_NULL, null=True, blank=True, related_name="class_posts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    images = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)  # Many-to-Many without extra fields

    def __str__(self):
        return self.title