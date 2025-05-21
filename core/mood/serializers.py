from rest_framework import serializers
from .models import ChildMood

class ChildMoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildMood
        fields = "__all__"