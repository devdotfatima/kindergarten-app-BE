from rest_framework import serializers
from datetime import date as dt
from .models import Nap
from attendance.models import Attendance

class NapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nap
        fields = "__all__"

    def validate(self, data):
        child = data.get("child")  # Use .get() to avoid KeyError
        date = data.get("date", dt.today())

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        # Check if the child has checked in on this date
        if not Attendance.objects.filter(child=child, date=date).exists():
            raise serializers.ValidationError({"error": "Child must be checked in before adding a meal."})
        
        """Ensure sleep_from is before sleep_to"""
        if data["sleep_from"] >= data["sleep_to"]:
            raise serializers.ValidationError({"error": "Sleep start time must be before sleep end time."})
        
        return data