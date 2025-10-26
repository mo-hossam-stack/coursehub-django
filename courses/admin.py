from django.contrib import admin
from .models import Course,Lesson
from django.utils.html import format_html

class lessonInline(admin.StackedInline):
    model = Lesson
    extra = 0
    readonly_fields = ['updated', 'public_id']
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [lessonInline]
    list_display = ['title', 'status', 'access']
    list_filter = ['status', 'access']
    fields = [ 'public_id','title', 'description', 'status', 'image', 'access', 'display_image']
    readonly_fields = [ 'public_id','display_image']

    def display_image(self, obj, *args, **kwargs):
        url = obj.image_admin_url
        if not url:
            return "No Image"
        return format_html(f"<img src='{url}' width='200' style='border-radius:8px;'/>")

    display_image.short_description = "Current Image"

#admin.site.register(Course, CourseAdmin)
