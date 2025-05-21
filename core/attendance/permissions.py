
from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanManageAttendance(BasePermission):
    """
    Permission for managing attendance records.
    
    - Superadmins: Full access.
    - Kindergarten Admins & Teachers: Full access if the child belongs to their kindergarten.
    - Parents: Can only view (SAFE_METHODS) attendance for their own child.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "superadmin":
            return True

        if request.user.role == "parent":
            return request.method in SAFE_METHODS

        # Check if admin or teacher is linked to a kindergarten
        if request.user.role in ["admin", "teacher"]:
            return hasattr(request.user, "kindergarten_admin") or hasattr(request.user, "teacher_profile")

        return False

    def has_object_permission(self, request, view, obj):
      user = request.user

      if user.role == "superadmin":
          return True

      if user.role == "parent":
          return request.method in SAFE_METHODS and obj.child.parent == user

      # Check if admin or teacher is assigned to the correct kindergarten
      if user.role in ["admin", "teacher"]:
          user_kindergarten = None
          
          if hasattr(user, "kindergarten_admin"):
              user_kindergarten = getattr(user.kindergarten_admin, "kindergarten", None)
          elif hasattr(user, "teacher_profile"):
              user_kindergarten = getattr(user.teacher_profile, "kindergarten", None)
          
          return obj.child.kindergarten == user_kindergarten

      return False