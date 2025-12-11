from django.db import models
import helpers
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
import uuid
helpers.cloudinary_init()
class AccessRequirement(models.TextChoices):
    ANYONE = "any", "Anyone"
    EMAIL_REQUIRED = "email", "Email required"

class PublishStatus(models.TextChoices):
    PUBLISHED = "publish", "Published"
    COMING_SOON = "soon", "Coming Soon"
    DRAFT = "draft", "Draft"

def get_public_id_prefix(instance, *args, **kwargs):
    if hasattr(instance, 'path'):
        path = instance.path
        if path.startswith("/"):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        return path
    public_id = instance.public_id
    model_class = instance.__class__
    model_name = model_class.__name__
    model_name_slug = slugify(model_name)
    if not public_id:
        return f"{model_name_slug}"
    return f"{model_name_slug}/{public_id}"

def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, 'get_display_name'):
        return instance.get_display_name()
    elif hasattr(instance, 'title'):
        return instance.title
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"

def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")[:5]
    if not title:
        return unique_id
    unique_id_short = unique_id[:5]
    slug = slugify(title)
    return f"{slug}--{unique_id_short}"




def handle_upload(instance, filename):
    return f"{filename}"
class Course(models.Model):
    title = models.CharField(max_length=120)
    public_id = models.CharField(max_length=130, blank=True, null=True,db_index=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    #image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    image = CloudinaryField(
        "image", 
        null=True, 
        public_id_prefix=get_public_id_prefix,
        display_name=get_display_name,
        tags=["course", "thumbnail"]
    )
    access = models.CharField(
        max_length=5,  
        choices=AccessRequirement.choices,
        default=AccessRequirement.EMAIL_REQUIRED
    )
    status = models.CharField(
        max_length=10, 
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
        )
    

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED
    
    def save(self, *args, **kwargs):
        # before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
        # after save


    def get_display_name(self):
        return f"{self.title} - Course"
    
    def get_absolute_url(self):
        return self.path
    
    @property
    def path(self):
        return f"/courses/{self.public_id}"


    def get_thumbnail(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self, 
            field_name='image',
            as_html=False,
            width=382
        )

    def get_display_image(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self, 
            field_name='image',
            as_html=False,
            width=750
        )
    
    def get_responsive_thumbnail(self):
        """Returns responsive srcset for course thumbnail"""
        if not self.image:
            return None
        return helpers.get_responsive_image_srcset(
            self,
            field_name='image',
            base_width=750
        )
    
    def get_mobile_thumbnail(self):
        """Returns mobile-optimized thumbnail"""
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self,
            field_name='image',
            width=640,
            lazy=True,
            responsive=False
        )
    """
    -lessons
        - title 
        - description
        - video
        - status : published, comming soon, draft
    """
# Lesson.objects.all() # lesson queryset -> all rows
# Lesson.objects.first()
# course_obj = Course.objects.first()
# course_qs = Course.objects.filter(id=course_obj.id)
# Lesson.objects.filter(course__id=course_obj.id)
# course_obj.lesson_set.all()
# lesson_obj = Lesson.objects.first()
# ne_course_obj = lesson_obj.course
# ne_course_lessons = ne_course_obj.lesson_set.all()
# lesson_obj.course_id
# course_obj.lesson_set.all().order_by("-title")
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # course_id 
    public_id = models.CharField(max_length=130, blank=True, null=True,db_index=True)

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    thumbnail = CloudinaryField("image", 
                public_id_prefix=get_public_id_prefix,
                display_name=get_display_name,
                blank=True, null=True,
                tags = [ 'thumbnail', 'lesson'],
                )
    video = CloudinaryField("video", 
            public_id_prefix=get_public_id_prefix,
            display_name=get_display_name,                
            blank=True, 
            null=True, 
            type = 'private',
            resource_type='video',
            tags = ['video', 'lesson'],
            )
    can_preview = models.BooleanField(default=False, help_text="If user does not have access to course, can they see this?")
    status = models.CharField(
        max_length=10, 
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ['order', '-updated']
    
    def save(self, *args, **kwargs):
        # before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
        # after save
    
    def get_absolute_url(self):
        return self.path
    @property
    def path(self):
        course_path = self.course.path
        if course_path.endswith("/"):
            course_path = course_path[:-1]
        return f"{course_path}/lessons/{self.public_id}"
    

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED
    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"
    
    @property
    def is_coming_soon(self):
        return self.status == PublishStatus.COMING_SOON
    @property
    def has_video(self):
        return self.video is not None
    def get_thumbnail(self):
        width = 382
        if self.thumbnail:
            return helpers.get_cloudinary_image_object(
                self, 
                field_name='thumbnail',
                format='jpg',
                as_html=False,
                width=width
            )
        elif self.video:
            return helpers.get_cloudinary_image_object(
            self, 
            field_name='video',
            format='jpg',
            as_html=False,
            width=width
        )
        return None
    
    def get_responsive_thumbnail(self):
        """Returns responsive srcset for lesson thumbnail"""
        field = 'thumbnail' if self.thumbnail else 'video'
        if field == 'video' and not self.video:
            return None
        return helpers.get_responsive_image_srcset(
            self,
            field_name=field,
            base_width=382
        )
    
    def get_video_poster(self):
        """Returns optimized video poster image"""
        if not self.video:
            return None
        return helpers.get_video_poster_image(
            self,
            field_name='video',
            time_offset=0
        )
    
    def get_mobile_video(self):
        """Returns mobile-optimized video player"""
        if not self.video:
            return None
        return helpers.get_cloudinary_video_object_mobile(
            self,
            field_name='video',
            network_quality='auto'
        )