from rest_framework import serializers
from .models import Hygiene

class HygieneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hygiene
        fields = "__all__"

    def validate(self, data):
        child = data.get("child")

        if not child:
            raise serializers.ValidationError({"child": "This field is required."})

        return data