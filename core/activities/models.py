from django.db import models
from children.models import Children
from kindergarten.models import KindergartenClass
from datetime import datetime


class Activity(models.Model):
    name = models.CharField(max_length=255)
    time = models.DateTimeField(default=datetime.now)
    children = models.ManyToManyField(Children, related_name="children_activities")
    class_id = models.ForeignKey(KindergartenClass, on_delete=models.CASCADE, related_name="class_activities")
    activity_image = models.TextField( null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.time.strftime('%Y-%m-%d %H:%M')}"

