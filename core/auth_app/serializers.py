from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import User 
from kindergarten.models import Kindergarten,Teacher


class UserProfileSerializer(serializers.ModelSerializer):
    kindergarten_id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'profile_picture', 'fcm_token', 'kindergarten_id',     'full_name'
        ]

    def get_kindergarten_id(self, obj):
        # Only include kindergarten_id for teachers
        if obj.role == 'teacher':
            # Get the related teacher profile and return the kindergarten id
            try:
                teacher = obj.teacher_profile
                return teacher.kindergarten.id
            except Teacher.DoesNotExist:
                return None  # Return None if no teacher profile exists for the user
        return None  # Return None if the user is not a teacher
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("email", "username", "role", "password","is_superuser") 

class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)
  fcm_token=serializers.CharField(write_only=True, required=False, allow_blank=True, default='')


class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "username", "profile_picture"]
        extra_kwargs = {"role": {"default": "admin"}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data['role'] = 'admin'
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ParentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "role", "username", "profile_picture"]
        extra_kwargs = {"role": {"default": "parent"}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data['role'] = 'parent'
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TeacherRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    kindergarten_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password","role", "username", "profile_picture","kindergarten_id"]
        extra_kwargs = {"role": {"default": "teacher"}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        kindergarten_id = validated_data.pop("kindergarten_id")

        try:
            kindergarten = Kindergarten.objects.get(id=kindergarten_id)
        except Kindergarten.DoesNotExist:
            raise serializers.ValidationError({"kindergarten_id": "Invalid kindergarten ID"})

        validated_data['role'] = 'teacher'
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        Teacher.objects.create(user=user, kindergarten=kindergarten)
        return user


class PinSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numbers.")
        return value


class PinLoginSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)
    fcm_token=serializers.CharField(write_only=True, required=False, allow_blank=True, default='')

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numbers.")
        return value


class SuperAdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    kindergarten_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'profile_picture', 'fcm_token', 'kindergarten_id',
            'date_joined',
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_kindergarten_id(self, obj):
        if obj.role == 'teacher':
            try:
                return obj.teacher_profile.kindergarten.id
            except Exception:
                return None
        if obj.role == 'admin':
            try:
                return obj.kindergarten_admin.kindergarten.id
            except Exception:
                return None
        return None


class SuperAdminEditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture', 'fcm_token']


class UserRoleChangeSerializer(serializers.Serializer):
    VALID_ROLES = ['parent', 'teacher', 'admin', 'superadmin']
    role = serializers.ChoiceField(choices=VALID_ROLES)


class AdminCreateParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture']

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        password = get_random_string(12)
        validated_data['role'] = 'parent'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user, password


class AdminCreateTeacherSerializer(serializers.ModelSerializer):
    kindergarten_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture', 'kindergarten_id']

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        from kindergarten.models import Kindergarten, Teacher as TeacherModel
        kindergarten_id = validated_data.pop('kindergarten_id')
        try:
            kindergarten = Kindergarten.objects.get(id=kindergarten_id)
        except Kindergarten.DoesNotExist:
            raise serializers.ValidationError({'kindergarten_id': 'Invalid kindergarten ID'})
        password = get_random_string(12)
        validated_data['role'] = 'teacher'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        TeacherModel.objects.create(user=user, kindergarten=kindergarten)
        return user, password


class AdminCreateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture']

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        password = get_random_string(12)
        validated_data['role'] = 'admin'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user, password