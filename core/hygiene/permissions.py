from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanManageHygieneActivities(BasePermission):
    """
    Custom permission to allow only relevant users to manage meals.

    - Superadmins: Full access to all meals.
    - Admins: Can manage meals only for children in their kindergarten.
    - Teachers: Can manage meals only for children in their class.
    - Parents: No write access (can only view meals for their own child).
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "superadmin":
            return True

        if request.user.role == "parent":
            return request.method in SAFE_METHODS

        # Check if the user is an admin or teacher linked to a kindergarten
        if request.user.role in ["admin", "teacher"]:
            return hasattr(request.user, "kindergarten_admin") or hasattr(request.user, "teacher_profile")

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "superadmin":
            return True  # Superadmins have full access

        if user.role == "parent":
            return request.method in SAFE_METHODS and obj.child.parent == user

        if user.role == "admin":
            return hasattr(user, "kindergarten_admin") and obj.child.kindergarten == user.kindergarten_admin.kindergarten

        if user.role == "teacher":
            if hasattr(user, "teacher_profile"):
                teacher_classes = user.teacher_profile.teacher_classes.all()
                return any(tc.class_id == obj.child.class_id for tc in teacher_classes)

        return False