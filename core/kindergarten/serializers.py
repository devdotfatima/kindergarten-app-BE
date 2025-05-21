from rest_framework import serializers
from .models import Kindergarten,KindergartenAdmin,KindergartenClass,TeacherClass,Teacher
from django.contrib.auth import get_user_model


User = get_user_model()


class KindergartenAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = KindergartenAdmin
        fields = ['user', 'kindergarten']

    def validate_user(self, value):
        """
        Ensure the user is of role 'admin' and exists in the users table.
        """
        if value.role != 'admin':
            raise serializers.ValidationError("Only admins can be assigned to kindergartens.")
        return value


class AttachAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    kindergarten_id = serializers.IntegerField()

    class Meta:
        model = KindergartenAdmin
        fields = ['user_id', 'kindergarten_id']

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user_id'])
        kindergarten = Kindergarten.objects.get(id=validated_data['kindergarten_id'])

        # Create a KindergartenAdmin object to attach the admin to the kindergarten
        kindergarten_admin = KindergartenAdmin.objects.create(user=user, kindergarten=kindergarten)
        return kindergarten_admin


class DetachAdminSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    kindergarten_id = serializers.IntegerField()


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = KindergartenClass
        fields = '__all__'


class TeacherClassSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_id.name", read_only=True)
    kindergarten_name = serializers.CharField(source="class_id.kindergarten.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.user.get_full_name", read_only=True)  # Fetch teacher name

    class Meta:
        model = TeacherClass
        fields = ["id", "teacher", "teacher_name", "class_id", "class_name", "kindergarten_name"]

class TeacherSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    profile_picture = serializers.CharField(source="user.profile_picture", read_only=True)
    kindergarten_name = serializers.CharField(source="kindergarten.name", read_only=True)
    classes = TeacherClassSerializer(source="teacher_classes", many=True, read_only=True)  # Fetch all assigned classes

    class Meta:
        model = Teacher
        fields = ["id", "email", "full_name", "profile_picture", "kindergarten", "kindergarten_name", "classes"]

class KindergartenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kindergarten
        fields = ["id", "name", "location"]
        ref_name = "KindergartenKindergarten"