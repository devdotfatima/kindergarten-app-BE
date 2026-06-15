from rest_framework import serializers
from .models import Nap

class NapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nap
        fields = "__all__"

    def validate(self, data):
        child = data.get("child")  # Use .get() to avoid KeyError

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        """Ensure sleep_from is before sleep_to"""
        if data["sleep_from"] >= data["sleep_to"]:
            raise serializers.ValidationError({"error": "Sleep start time must be before sleep end time."})

        return data