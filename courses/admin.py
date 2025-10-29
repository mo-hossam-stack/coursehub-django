from django.contrib import admin
from .models import Course,Lesson
from django.utils.html import format_html
import helpers
class lessonInline(admin.StackedInline):
    model = Lesson
    extra = 0

    readonly_fields = [
        'public_id', 
        'updated', 
        'display_image',
        'display_video',
    ]

    def display_image(self, obj, *args, **kwargs):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='thumbnail',
            width=200
        )
        return format_html(f"<img src={url} />")

    display_image.short_description = "Current Image"

    def display_video(self, obj, *args, **kwargs):
        video_embed_html = helpers.get_cloudinary_video_object(
            obj, 
            field_name='video',
            as_html=True,
            width=550
        )
        return video_embed_html

    display_video.short_description = "Current Video"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [lessonInline]
    list_display = ['title', 'status', 'access']
    list_filter = ['status', 'access']
    fields = [ 'public_id','title', 'description', 'status', 'image', 'access', 'display_image']
    readonly_fields = [ 'public_id','display_image']

    def display_image(self, obj, *args, **kwargs):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='image',
            width=200
        )
        return format_html(f"<img src={url} />")

    display_image.short_description = "Current Image"

#admin.site.register(Course, CourseAdmin)
