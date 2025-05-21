from rest_framework import serializers
from datetime import date as dt
from .models import Hygiene
from attendance.models import Attendance

class HygieneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hygiene
        fields = "__all__"

    def validate(self, data):
        child = data.get("child") 
        date = data.get("date", dt.today())

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        # Check if the child has checked in on this date
        if not Attendance.objects.filter(child=child, date=date).exists():
            raise serializers.ValidationError({"error": "Child must be checked in before adding a hygiene activity."})
        
        return data