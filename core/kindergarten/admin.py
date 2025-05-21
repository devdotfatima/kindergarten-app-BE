from django.contrib import admin
from .models import Kindergarten, KindergartenAdmin, Teacher, KindergartenClass, TeacherClass
from children.models import Children

class KindergartenAdminPanel(admin.ModelAdmin):
    list_display = ("id", "name", "kindergarten_admin")  
    search_fields = ("name", "admin_user__user__email")  
    list_filter = ("admin_user",) 

    def kindergarten_admin(self, obj):
        return obj.admin_user.user.email if obj.admin_user else "No Admin"
    kindergarten_admin.short_description = "Kindergarten Admin"


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher_name", "kindergarten_name", "admin_email")  
    search_fields = ("user__email", "user__username", "kindergarten__name")
    list_filter = ("kindergarten",)

    def teacher_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    teacher_name.short_description = "Teacher Name"

    def kindergarten_name(self, obj):
        return obj.kindergarten.name
    kindergarten_name.short_description = "Kindergarten"

    def admin_email(self, obj):
        admin = KindergartenAdmin.objects.filter(kindergarten=obj.kindergarten).first()
        return admin.user.email if admin else "No Admin"
    admin_email.short_description = "Admin Email"


class KindergartenClassAdmin(admin.ModelAdmin):
    list_display = ("id", "class_name", "kindergarten_name", "teacher_names", "total_children_enrolled")  
    search_fields = ("name", "kindergarten__name")
    list_filter = ("kindergarten",)

    def class_name(self, obj):
        return obj.name
    class_name.short_description = "Class Name"

    def kindergarten_name(self, obj):
        return obj.kindergarten.name
    kindergarten_name.short_description = "Kindergarten"

    def teacher_names(self, obj):
      teachers = TeacherClass.objects.filter(class_id=obj).select_related("teacher__user")
      teacher_list = [teacher.teacher.user.get_full_name() or teacher.teacher.user.username for teacher in teachers]
      return ", ".join(teacher_list) if teacher_list else "No Teacher Assigned"
    teacher_names.short_description = "Teachers"


    def total_children_enrolled(self, obj):
        return Children.objects.filter(class_id=obj).count()
    total_children_enrolled.short_description = "Total Enrolled Children"

admin.site.register(Kindergarten, KindergartenAdminPanel)
admin.site.register(KindergartenAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(TeacherClass)
admin.site.register(KindergartenClass, KindergartenClassAdmin)
