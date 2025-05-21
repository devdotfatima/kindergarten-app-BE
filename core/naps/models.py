from django.db import models
from children.models import Children
from datetime import date, datetime

class Nap(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name="naps")
    date = models.DateField(default=date.today)
    sleep_from = models.TimeField()
    sleep_to = models.TimeField()

    def __str__(self):
        return f"{self.child.name} - {self.date} ({self.sleep_from} - {self.sleep_to})"
