from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanManageChildMood(BasePermission):
    """
    Superadmins can manage all moods.
    Admins can manage moods for children in their kindergarten.
    Teachers can manage moods for children in their assigned class.
    Parents can only view their child’s mood but cannot modify it.
    """

    def has_permission(self, request, view):
        """Check if the user is authenticated for this endpoint."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Grant permissions based on user roles."""
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