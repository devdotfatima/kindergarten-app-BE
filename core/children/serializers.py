
from rest_framework import serializers
from .models import Children
from kindergarten.models import Kindergarten, KindergartenClass
from auth_app.models import User



class KindergartenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kindergarten
        fields = ['id', 'name','location']  # Add other necessary fields
        ref_name = "ChildrenKindergarten" 

class KindergartenClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = KindergartenClass
        fields = ["id", "name", "kindergarten"]

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', ]  # Add necessary fields

class ChildrenSerializer(serializers.ModelSerializer):
    # Read-only fields (Nested serializers for GET)
    kindergarten_details = KindergartenSerializer(source="kindergarten", read_only=True)
    class_details = KindergartenClassSerializer(source="class_id", read_only=True)
    parent_details = ParentSerializer(source="parent", read_only=True)  # Add parent details

    # Write-only fields (IDs for POST/PUT)
    kindergarten = serializers.PrimaryKeyRelatedField(queryset=Kindergarten.objects.all(), write_only=True)
    class_id = serializers.PrimaryKeyRelatedField(queryset=KindergartenClass.objects.all(), required=False, allow_null=True, write_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # Keep writable

    class Meta:
        model = Children
        fields = [
            'id', 'name', 'date_of_birth', 'kindergarten', 'kindergarten_details',
            'class_id', 'class_details', 'profile_picture', 'parent', 'parent_details','bio'
        ]
