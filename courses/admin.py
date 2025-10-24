from django.contrib import admin
from .models import Course
from django.utils.html import format_html

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'access']
    list_filter = ['status', 'access']
    fields = [ 'title', 'description', 'status', 'image', 'access', 'display_image']
    readonly_fields = [ 'display_image']

    def display_image(self, obj, *args, **kwargs):
        url = obj.image_admin
        if not url:
            return "No Image"
        return format_html(f"<img src='{url}' width='200' style='border-radius:8px;'/>")

    display_image.short_description = "Current Image"

#admin.site.register(Course, CourseAdmin)
