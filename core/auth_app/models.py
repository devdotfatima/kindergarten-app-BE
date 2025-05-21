from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for authentication with email instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        # Generate a username if not provided
        if not extra_fields.get("username"):
            base_username = slugify(email.split("@")[0])
            unique_suffix = uuid.uuid4().hex[:6]  # Generate unique suffix
            extra_fields["username"] = f"{base_username}-{unique_suffix}"

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Ensure superadmins have correct flags and a username."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("parent", "Parent"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
        ("superadmin", "Superadmin"),
    ]

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="parent")
    pin = models.CharField(max_length=128, blank=True, null=True) 
    profile_picture = models.TextField( null=True, blank=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()  

    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = []  

    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)

    def __str__(self):
        return self.email


@receiver(pre_save, sender=User)
def set_superadmin_flags(sender, instance, **kwargs):
    """Ensure superadmin role automatically gets superuser permissions."""
    
    if instance.role == "superadmin":
        instance.is_superuser = True
        instance.is_staff = True
    elif instance.role in ["parent", "teacher", "admin"]:
        instance.is_superuser = False