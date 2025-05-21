from django.contrib import admin
from .models import Activity

class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "get_class_name", "get_children_names", "time")
    search_fields = ("name", "class_id__name", "children__first_name", "children__last_name")
    list_filter = ("class_id", "time")

    def get_class_name(self, obj):
        return obj.class_id.name  # Assuming class_id has a 'name' field
    get_class_name.short_description = "Class Name"

    def get_children_names(self, obj):
        return ", ".join([child.name for child in obj.children.all()])
    get_children_names.short_description = "Children"



admin.site.register(Activity, ActivityAdmin)