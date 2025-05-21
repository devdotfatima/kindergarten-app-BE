from rest_framework import permissions
from .models import KindergartenAdmin

from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to superadmins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superadmin"

class KindergartenPermission(permissions.BasePermission):
  
    """
    Custom permission to restrict kindergarten actions based on user role.
    """

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser or user.role == "superadmin":
            return True

        # Admins can only access their assigned kindergarten
        if user.role == "admin":
            return view.action in ["retrieve", "update", "partial_update", "list"]

        # Everyone else is denied access
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.role == "superadmin":
            return True

        if user.role == "admin":
            try:
                return obj == user.kindergarten_admin.kindergarten
            except KindergartenAdmin.DoesNotExist:
                return False

        return False