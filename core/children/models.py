
from django.db import models
from auth_app.models import User
from kindergarten.models import Kindergarten, KindergartenClass

class Children(models.Model):
    name = models.CharField(max_length=250)
    bio = models.CharField(max_length=500,null=True,)
    date_of_birth = models.DateField()
    kindergarten = models.ForeignKey(Kindergarten, on_delete=models.CASCADE)
    class_id = models.ForeignKey(KindergartenClass, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children")
    profile_picture = models.TextField( null=True, blank=True)

    def __str__(self):
        return self.name