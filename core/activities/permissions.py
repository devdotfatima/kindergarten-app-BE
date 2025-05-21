
from rest_framework import  permissions

class ActivityPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in ['superadmin', 'admin', 'teacher']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
     
        if request.user.role == 'superadmin':
            return True
        elif request.user.role == 'admin' and obj.class_id.kindergarten == request.user.kindergarten_admin.kindergarten:
            return True
        elif request.user.role == 'teacher':
            teacher_classes = request.user.teacher_profile.teacher_classes.all()
            return any(tc.class_id == obj.class_id for tc in teacher_classes)
         
        return False


