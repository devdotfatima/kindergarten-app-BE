from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "full_name", "role", "profile_picture_tag", "is_staff", "is_superuser")
    search_fields = ("email", "role", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "role", "profile_picture")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["widgets"] = {"username": admin.widgets.AdminTextInputWidget(attrs={"readonly": "readonly"})}
        return super().get_form(request, obj, **kwargs)

    def full_name(self, obj):
        """Concatenates first name and last name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    full_name.short_description = "Full Name"

    def profile_picture_tag(self, obj):
        """Displays the profile picture as an image in the admin panel"""
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture)
        return "No Image"
    profile_picture_tag.short_description = "Profile Picture"


admin.site.register(User, CustomUserAdmin)