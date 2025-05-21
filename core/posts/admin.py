from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "kindergarten_name", "class_name", "likes_count", "created_at","id")
    search_fields = ("title", "kindergarten__name", "class_id__name")
    list_filter = ("kindergarten", "class_id", "created_at")

    def kindergarten_name(self, obj):
        return obj.kindergarten.name
    kindergarten_name.admin_order_field = "kindergarten"  # Allows sorting
    kindergarten_name.short_description = "Kindergarten"

    def class_name(self, obj):
        return obj.class_id.name if obj.class_id else "No Class"
    class_name.admin_order_field = "class_id"
    class_name.short_description = "Class"

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"

admin.site.register(Post, PostAdmin)