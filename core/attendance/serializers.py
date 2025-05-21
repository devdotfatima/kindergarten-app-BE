from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    child_details = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["id", "child", "child_details", "date", "check_in_time", "check_out_time"]

    def get_child_details(self, obj):
        return {"id": obj.child.id, "name": obj.child.name}