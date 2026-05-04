from rest_framework import serializers
from .models import Kindergarten, KindergartenAdmin, KindergartenClass, TeacherClass, Teacher, Section
from django.contrib.auth import get_user_model


User = get_user_model()


class KindergartenAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = KindergartenAdmin
        fields = ['user', 'kindergarten']

    def validate_user(self, value):
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
        kindergarten_admin = KindergartenAdmin.objects.create(user=user, kindergarten=kindergarten)
        return kindergarten_admin


class DetachAdminSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    kindergarten_id = serializers.IntegerField()


class SectionSerializer(serializers.ModelSerializer):
    kindergarten_name = serializers.CharField(source='kindergarten.name', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'kindergarten', 'kindergarten_name']


class ClassSerializer(serializers.ModelSerializer):
    kindergarten_name = serializers.CharField(source='kindergarten.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)

    class Meta:
        model = KindergartenClass
        fields = ['id', 'name', 'kindergarten', 'kindergarten_name', 'section', 'section_name']


class TeacherClassSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_id.name", read_only=True)
    kindergarten_name = serializers.CharField(source="class_id.kindergarten.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.user.get_full_name", read_only=True)

    class Meta:
        model = TeacherClass
        fields = ["id", "teacher", "teacher_name", "class_id", "class_name", "kindergarten_name"]


class TeacherSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    profile_picture = serializers.CharField(source="user.profile_picture", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    kindergarten_name = serializers.CharField(source="kindergarten.name", read_only=True)
    classes = TeacherClassSerializer(source="teacher_classes", many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id", "user_id", "email", "full_name", "first_name", "last_name",
            "phone_number", "profile_picture", "kindergarten", "kindergarten_name", "classes"
        ]


class KindergartenSerializer(serializers.ModelSerializer):
    admin_name = serializers.SerializerMethodField()
    admin_email = serializers.SerializerMethodField()

    def get_admin_name(self, obj):
        try:
            name = obj.admin_user.user.get_full_name()
            return name or obj.admin_user.user.email
        except Exception:
            return None

    def get_admin_email(self, obj):
        try:
            return obj.admin_user.user.email
        except Exception:
            return None

    class Meta:
        model = Kindergarten
        fields = ["id", "name", "location", "admin_name", "admin_email"]
        ref_name = "KindergartenKindergarten"
