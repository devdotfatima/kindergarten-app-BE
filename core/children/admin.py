from django.contrib import admin
from .models import Children

class ChildrenAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent_email", "kindergarten_name", "class_name")  
    search_fields = ("name", "parent__email", "kindergarten__name")  
    list_filter = ("kindergarten", "class_id")  

    def parent_email(self, obj):
        return obj.parent.email if obj.parent else "No Parent"
    parent_email.short_description = "Parent Email"

    def kindergarten_name(self, obj):
        return obj.kindergarten.name if obj.kindergarten else "No Kindergarten"
    kindergarten_name.short_description = "Kindergarten"

    def class_name(self, obj):
        return obj.class_id.name if obj.class_id else "No Class"
    class_name.short_description = "Class"

admin.site.register(Children, ChildrenAdmin)