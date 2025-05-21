from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanManagePosts(BasePermission):
    """
    Custom permission for managing posts.

    - Superadmins: Full access to all posts.
    - Admins: Can manage posts only for their kindergarten.
    - Teachers: Can manage posts only for their assigned class.
    - Parents: Can only view posts related to their child's class.
    """

    def has_permission(self, request, view):
        """Global permission check before accessing the view."""
        if not request.user.is_authenticated:
            return False

        if request.user.role == "superadmin":
            return True  # Superadmins can do anything

        if request.user.role == "parent":
            return request.method in SAFE_METHODS  # Parents can only view posts

        # Admins and teachers can manage posts related to their kindergarten or class
        if request.user.role in ["admin", "teacher"]:
            return hasattr(request.user, "kindergarten_admin") or hasattr(request.user, "teacher_profile")

        return False

    def has_object_permission(self, request, view, obj):
        """Object-level permission check for individual posts."""
        user = request.user

        if user.role == "superadmin":
            return True  # Superadmins have full access

        if user.role == "parent":
            return request.method in SAFE_METHODS and user.parent.children.filter(class_id=obj.class_id).exists()

        if user.role == "admin":
            return hasattr(user, "kindergarten_admin") and obj.kindergarten == user.kindergarten_admin.kindergarten

        if user.role == "teacher":
            if hasattr(user, "teacher_profile"):
                teacher_classes = request.user.teacher_profile.teacher_classes.all()
                return any(obj.class_id == obj.class_id for tc in teacher_classes)

        return False