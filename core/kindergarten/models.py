from django.db import models
from django.contrib.auth import get_user_model

class Kindergarten(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField()

    def __str__(self):
        return self.name


User = get_user_model()


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    kindergarten = models.ForeignKey(Kindergarten, on_delete=models.CASCADE, related_name="teachers")

    def __str__(self):
        return f"{self.user.email} - {self.kindergarten.name}"


class KindergartenClass(models.Model):
    name = models.CharField(max_length=255)
    kindergarten = models.ForeignKey(Kindergarten, on_delete=models.CASCADE, related_name="classes")

    def __str__(self):
        return f"{self.name} - {self.kindergarten.name}"


class TeacherClass(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_classes")
    class_id = models.ForeignKey(KindergartenClass, on_delete=models.CASCADE, related_name="kindergarten_class")

    class Meta:
        unique_together = ('teacher', 'class_id')

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.class_id.name}"
        

class KindergartenAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kindergarten_admin')
    kindergarten = models.OneToOneField(Kindergarten, on_delete=models.CASCADE, related_name='admin_user')

    def __str__(self):
        return f'{self.user.username} is the admin of {self.kindergarten.name}'