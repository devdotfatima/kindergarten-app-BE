from django.db import models
from datetime import date
from children.models import Children  

class Attendance(models.Model):
    child = models.ForeignKey(Children, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=date.today) # Default to current date
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)  # Optional check-out

    def __str__(self):
        return f"{self.child.name} - {self.date}"