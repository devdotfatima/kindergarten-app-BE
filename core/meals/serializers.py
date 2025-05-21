from rest_framework import serializers
from datetime import date as dt
from .models import Meal
from attendance.models import Attendance

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = "__all__"

    def validate(self, data):
        child = data.get("child")  # Use .get() to avoid KeyError
        date = data.get("date", dt.today())

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        # Check if the child has checked in on this date
        if not Attendance.objects.filter(child=child, date=date).exists():
            raise serializers.ValidationError({"error": "Child must be checked in before adding a meal."})
        
        return data