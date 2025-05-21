from django.db import models
from children.models import Children
from datetime import date, datetime


class Hygiene(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name="hygiene_records")
    activity = models.CharField(max_length=50) 
    date = models.DateField(default=date.today) 
    hygiene_activity_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.hygiene_activity_time:
            self.hygiene_activity_time = datetime.now().time()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.name} - {self.activity} ({self.date})"