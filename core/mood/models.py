from django.db import models
from children.models import Children
from django.utils import timezone



class ChildMood(models.Model):
    class MoodChoices(models.TextChoices):
        HAPPY = "happy", "Happy"
        CALM = "calm", "Calm"
        SAD = "sad", "Sad"
        TIRED = "tired", "Tired"
        SLEEPY = "sleepy", "Sleepy"
        ANGRY = "angry", "Angry"
        ANNOYED = "annoyed", "Annoyed"
        FRUSTRATED = "frustrated", "Frustrated"

    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name="moods")

    mood = models.CharField(max_length=20, choices=MoodChoices.choices)


    date = models.DateField(default=timezone.now)  # ✅ Correct way

    def __str__(self):
        return f"{self.child.name} - {self.mood} ({self.date})"