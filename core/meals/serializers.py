from rest_framework import serializers
from .models import Meal

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = "__all__"

    def validate(self, data):
        child = data.get("child")  # Use .get() to avoid KeyError

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        return data