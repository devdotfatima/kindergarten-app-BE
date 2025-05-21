from django.db import models
from children.models import Children
from datetime import date, datetime

class Meal(models.Model):
    class AppetiteLevel(models.TextChoices):
        LOW = "low", "Low Appetite"
        NORMAL = "normal", "Normal Appetite"
        HIGH = "high", "High Appetite"

    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name="meals")
    date = models.DateField(default=date.today) 
    meal_description = models.TextField(null=True, blank=True)
    meal_title = models.CharField(max_length=150)
    intake_time = models.TimeField(null=True, blank=True)
    appetite_level = models.CharField(
        max_length=10,
        choices=AppetiteLevel.choices,
        default=AppetiteLevel.NORMAL  # Default to "Normal Appetite"
    )

    def save(self, *args, **kwargs):
        if not self.intake_time:
            self.intake_time = datetime.now().time()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.name} - {self.date} - {self.meal_title} ({self.get_appetite_level_display()})"