# Project Implementation Reference
## CourseHub Django Platform

Complete reference of all implemented features, endpoints, models, services, and components.

---

## 1. Features Overview

### 1.1 Core Features

| Feature | Status | Description |
|---------|--------|-------------|
| Course Management | ✅ Complete | Create, publish, and manage courses with thumbnails |
| Lesson Management | ✅ Complete | Video lessons with thumbnails, ordering, and status control |
| Email Verification | ✅ Complete | Passwordless authentication via email tokens & 6-digit OTP |
| Access Control | ✅ Complete | Public vs email-required content |
| Video Streaming | ✅ Complete | Cloudinary-powered adaptive video streaming |
| HTMX Integration | ✅ Complete | Dynamic partial page updates without full reloads |
| Responsive UI | ✅ Complete | TailwindCSS + Flowbite + DaisyUI components |
| Admin Panel | ✅ Complete | Custom admin with inline lesson editing and media previews |
| Security | ✅ Complete | Rate limiting, OTP invalidation, and secure session management |

### 1.2 Feature Timeline (from Git History)

| Date | Commit | Feature Added |
|------|--------|---------------|
| 2025-10-24 | `a0d9cfa` | Project initialization |
| 2025-10-24 | `d27a1c0` | Course model and migrations |
| 2025-10-24 | `b1a9580` | Cloudinary configuration |
| 2025-10-24 | `4c3d96c` | Cloudinary image hosting |
| 2025-10-25 | `4c18a7c` | Lesson model initialization |
| 2025-10-25 | `27dc08a` | Lesson media fields and admin inline |
| 2025-10-25 | `a2839f7` | Public ID generation for courses |
| 2025-10-26 | `477c246` | Slugify and path handling fixes |
| 2025-10-27 | `7002f29` | Cloudinary helpers decoupling |
| 2025-10-29 | `3eef0f7` | Cloudinary video object service |
| 2025-10-29 | `75ce3b9` | Cloudinary Video Player integration |
| 2025-10-30 | `6f8827a` | **Database migration: SQLite → MySQL** |
| 2025-11-04 | `951c8f0` | Service layer for courses and lessons |
| 2025-11-04 | `c2b32f0` | Template rendering from views |
| 2025-11-06 | `2cc3e44` | Video player rendering for users |
| 2025-11-16 | `8803a17` | **TailwindCSS v4 + DaisyUI + HTMX setup** |
| 2025-11-18 | `185da97` | Email verification models |
| 2025-11-18 | `a2015ef` | Gmail SMTP configuration |
| 2025-11-20 | `db315f0` | Email validation and verification events |
| 2025-11-23 | `7db0eab` | UUID-based verification links |
| 2025-11-23 | `bf25dd8` | Token verification service |
| 2025-11-24 | `e97333a` | Session enrichment with email ID |
| 2025-11-26 | `50fd3aa` | Email-required lesson access control |
| 2025-11-26 | `48b566b` | HTMX email login form |
| 2025-11-26 | `bbd097f` | Logout logic |
| 2025-11-27 | `c4d26a6` | Flowbite integration |
| 2025-11-27 | `3488947` | Login/logout views and URLs |
| 2025-11-27 | `1d40c9e` | Course list with thumbnails |
| 2025-12-01 | `0f9e447` | Video frame as lesson thumbnail fallback |

---

## 2. API Endpoints

### 2.1 Public Endpoints

| Method | URL Pattern | View Function | Description |
|--------|-------------|---------------|-------------|
| GET | `/` | `home_view` | Homepage with email form |
| GET | `/courses/` | `course_list_view` | List all published courses |
| GET | `/courses/<course_id>/` | `course_detail_view` | Course detail with lessons |
| GET | `/courses/<course_id>/lessons/<lesson_id>/` | `lesson_detail_view` | Lesson detail with video player |
| GET | `/login/` | `login_logout_template_view` | Login/logout page |
| GET | `/logout/` | `login_logout_template_view` | Same as login (shared template) |

### 2.2 Authentication Endpoints

| Method | URL Pattern | View Function | Description |
|--------|-------------|---------------|-------------|
| GET | `/verify-email/<uuid:token>/` | `verify_email_token_view` | Verify email token and set session |

### 2.3 HTMX Endpoints

| Method | URL Pattern | View Function | Description |
|--------|-------------|---------------|-------------|
| POST | `/hx/login/` | `email_token_login_view` | Submit email for verification (HTMX) |
| POST | `/hx/verify-otp/` | `content_views.verify_otp_view` | Verify 6-digit OTP code |
| POST | `/hx/resend-otp/` | `content_views.resend_otp_view` | Resend verification code (with rate limit) |
| POST | `/hx/logout/` | `logout_btn_hx_view` | Clear session and logout (HTMX) |

### 2.4 Admin Endpoints

| Method | URL Pattern | Description |
|--------|-------------|-------------|
| GET/POST | `/admin/` | Django admin panel |
| GET/POST | `/admin/courses/course/` | Course management |
| GET/POST | `/admin/courses/lesson/` | Lesson management (inline) |
| GET/POST | `/admin/emails/email/` | Email records |

---

## 3. Models & Fields

### 3.1 Course Model

**File**: [`courses/models.py`](file:///home/mhmd/Desktop/projects/coursehub-django/courses/models.py#L55-L102)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PK | Auto-generated primary key |
| `title` | CharField(120) | Required | Course title |
| `public_id` | CharField(130) | Unique, Indexed, Auto-generated | URL-safe slug (e.g., `django-basics--a3f9c`) |
| `description` | TextField | Optional | Course description |
| `image` | CloudinaryField | Optional | Course thumbnail (public) |
| `access` | CharField(5) | Choices: `any`, `email` | Access control level |
| `status` | CharField(10) | Choices: `publish`, `soon`, `draft` | Publication status |
| `timestamp` | DateTimeField | Auto-add | Creation timestamp |
| `updated` | DateTimeField | Auto-update | Last modification timestamp |

**Properties**:
- `is_published`: Returns `True` if status is `PUBLISHED`
- `path`: Returns `/courses/<public_id>`

**Methods**:
- `get_display_name()`: Returns `"{title} - Course"`
- `get_absolute_url()`: Returns `path` property
- `get_thumbnail()`: Returns Cloudinary URL (382px width)
- `get_display_image()`: Returns Cloudinary URL (750px width)
- `save()`: Auto-generates `public_id` if empty

### 3.2 Lesson Model

**File**: [`courses/models.py`](file:///home/mhmd/Desktop/projects/coursehub-django/courses/models.py#L141-L222)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PK | Auto-generated primary key |
| `course` | ForeignKey(Course) | CASCADE | Parent course |
| `public_id` | CharField(130) | Unique, Indexed, Auto-generated | URL-safe slug |
| `title` | CharField(120) | Required | Lesson title |
| `description` | TextField | Optional | Lesson description |
| `thumbnail` | CloudinaryField | Optional | Lesson thumbnail (public) |
| `video` | CloudinaryField | Optional, **Private** | Lesson video (signed URLs) |
| `can_preview` | BooleanField | Default: False | Allow preview without email |
| `status` | CharField(10) | Choices: `publish`, `soon`, `draft` | Publication status |
| `order` | IntegerField | Default: 0 | Display order |
| `timestamp` | DateTimeField | Auto-add | Creation timestamp |
| `updated` | DateTimeField | Auto-update | Last modification timestamp |

**Meta**:
- `ordering = ['order', '-updated']`

**Properties**:
- `path`: Returns `/courses/<course_public_id>/lessons/<public_id>`
- `requires_email`: Returns `True` if course access is `EMAIL_REQUIRED`
- `is_coming_soon`: Returns `True` if status is `COMING_SOON`
- `has_video`: Returns `True` if video field is not None

**Methods**:
- `get_display_name()`: Returns `"{title} - {course.get_display_name()}"`
- `get_absolute_url()`: Returns `path` property
- `get_thumbnail()`: Returns thumbnail URL or video frame (382px width)
- `save()`: Auto-generates `public_id` if empty

### 3.3 Email Model

**File**: [`emails/models.py`](file:///home/mhmd/Desktop/projects/coursehub-django/emails/models.py#L6-L10)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PK | Auto-generated primary key |
| `email` | EmailField | **Unique** | User email address |
| `active` | BooleanField | Default: True | Email active status |
| `timestamp` | DateTimeField | Auto-add | Creation timestamp |

### 3.4 EmailVerificationEvent Model

**File**: [`emails/models.py`](file:///home/mhmd/Desktop/projects/coursehub-django/emails/models.py#L13-L34)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PK | Auto-generated primary key |
| `parent` | ForeignKey(Email) | SET_NULL, Nullable | Associated email record |
| `email` | EmailField | Required | Email address (denormalized) |
| `token` | UUIDField | Default: uuid.uuid1 | Verification token |
| `attempts` | IntegerField | Default: 0 | Verification attempt counter |
| `last_attempt_at` | DateTimeField | Optional | Last verification attempt |
| `expired` | BooleanField | Default: False | Token expiration flag |
| `expired_at` | DateTimeField | Optional | Expiration timestamp |
| `timestamp` | DateTimeField | Auto-add | Creation timestamp |

**Methods**:
- `get_link()`: Returns `{BASE_URL}/verify-email/{token}/`

---

## 4. Services & Business Logic

### 4.1 Course Services

**File**: [`courses/services.py`](file:///home/mhmd/Desktop/projects/coursehub-django/courses/services.py)

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `get_publish_courses()` | None | QuerySet[Course] | All published courses |
| `get_course_detail(course_id)` | `course_id: str` | Course \| None | Single published course by public_id |
| `get_course_lessons(course_obj)` | `course_obj: Course` | QuerySet[Lesson] | Published/coming-soon lessons for course |
| `get_lesson_detail(course_id, lesson_id)` | `course_id: str`<br>`lesson_id: str` | Lesson \| None | Single lesson by course and lesson public_id |

**Design Pattern**: Service layer separates business logic from views.

### 4.2 Email Services

**File**: [`emails/services.py`](file:///home/mhmd/Desktop/projects/coursehub-django/emails/services.py)

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `verify_email(email)` | `email: str` | bool | Check if email exists and is inactive |
| `get_verification_email_message(verification_instance, as_html)` | `verification_instance: EmailVerificationEvent`<br>`as_html: bool` | str | Generate email message with verification link |
| `start_verification_event(email)` | `email: str` | tuple[EmailVerificationEvent, bool] | Create verification event and send email |
| `send_verification_email(verify_obj_id)` | `verify_obj_id: int` | bool | Send verification email via SMTP |
| `verify_token(token, max_attempts)` | `token: UUID`<br>`max_attempts: int = 5` | tuple[bool, str, Email \| None] | Validate token and return result |
| `verify_otp(email, otp)` | `email: str`<br>`otp: str` | tuple[bool, str, Email \| None] | Validate 6-digit OTP |
| `check_rate_limit(email)` | `email: str` | bool | Check if email sending limit exceeded |

**Token Validation Logic**:
1. Check token exists
2. Check not expired
3. Check attempts < max_attempts
4. Increment attempts
5. Expire if attempts > max_attempts
6. Return success/failure with message

### 4.3 Cloudinary Helpers

**File**: [`helpers/_cloudinary/services.py`](file:///home/mhmd/Desktop/projects/coursehub-django/helpers/_cloudinary/services.py)

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `get_cloudinary_image_object(instance, field_name, as_html, width, format)` | `instance: Model`<br>`field_name: str = "image"`<br>`as_html: bool = False`<br>`width: int = 1200`<br>`format: str \| None` | str | Get Cloudinary image URL or HTML |
| `get_cloudinary_video_object(instance, field_name, as_html, width, height, sign_url, ...)` | `instance: Model`<br>`field_name: str = "video"`<br>`as_html: bool = False`<br>`width: int \| None`<br>`height: int \| None`<br>`sign_url: bool = True`<br>`fetch_format: str = "auto"`<br>`quality: str = "auto"`<br>`controls: bool = True`<br>`autoplay: bool = True` | str | Get Cloudinary video URL or player embed |

**Cloudinary Config**:

**File**: [`helpers/_cloudinary/config.py`](file:///home/mhmd/Desktop/projects/coursehub-django/helpers/_cloudinary/config.py)

```python
def cloudinary_init():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_PUBLIC_API_KEY,
        api_secret=CLOUDINARY_SECRET_API_KEY,
        secure=True
    )
```

---

## 5. Views & Controllers

### 5.1 Course Views

**File**: [`courses/views.py`](file:///home/mhmd/Desktop/projects/coursehub-django/courses/views.py)

#### `course_list_view(request)`
- **URL**: `/courses/`
- **Template**: `courses/list.html` (full) or `courses/snippets/list-display.html` (HTMX)
- **Context**: `object_list` (all published courses)
- **HTMX**: Returns first 3 courses as snippet

#### `course_detail_view(request, course_id)`
- **URL**: `/courses/<course_id>/`
- **Template**: `courses/detail.html`
- **Context**: 
  - `object`: Course instance
  - `lessons_queryset`: Published/coming-soon lessons
- **Error**: Raises `Http404` if course not found

#### `lesson_detail_view(request, course_id, lesson_id)`
- **URL**: `/courses/<course_id>/lessons/<lesson_id>/`
- **Templates**:
  - `courses/email-required.html` (no email in session)
  - `courses/lesson-coming-soon.html` (no video)
  - `courses/lesson.html` (video available)
- **Context**:
  - `object`: Lesson instance
  - `video_embed`: Cloudinary Video Player HTML (if video available)
- **Access Control**: Checks `session['email_id']` if `lesson.requires_email`
- **Redirect**: Stores `session['next_url']` for post-login redirect

### 5.2 Email Views

**File**: [`emails/views.py`](file:///home/mhmd/Desktop/projects/coursehub-django/emails/views.py)

#### `email_token_login_view(request)`
- **URL**: `/hx/login/`
- **Method**: POST (HTMX only)
- **Template**: `emails/hx/form.html`
- **Form**: `EmailForm`
- **Logic**:
  1. Validate email
  2. Call `start_verification_event(email)`
  3. Return success message
  4. Reset form
- **Redirect**: Non-HTMX requests redirect to `/`

#### `verify_email_token_view(request, token)`
- **URL**: `/verify-email/<uuid:token>/`
- **Method**: GET
- **Logic**:
  1. Call `verify_token(token)`
  2. If valid: Set `session['email_id']`, redirect to `next_url`
  3. If invalid: Clear session, show error, redirect to `/login/`
- **Messages**: Uses Django messages framework

#### `logout_btn_hx_view(request)`
- **URL**: `/hx/logout/`
- **Method**: POST (HTMX only)
- **Template**: `emails/hx/logout-btn.html`
- **Logic**:
  1. Delete `session['email_id']`
  2. Return HTMX redirect to `/`

### 5.3 Home Views

**File**: [`home/views.py`](file:///home/mhmd/Desktop/projects/coursehub-django/home/views.py)

#### `home_view(request)`
- **URL**: `/`
- **Template**: `home.html`
- **Form**: `EmailForm`
- **Logic**: Same as `email_token_login_view` (legacy, pre-HTMX)

#### `login_logout_template_view(request)`
- **URL**: `/login/` or `/logout/`
- **Template**: `auth/login-logout.html`
- **Purpose**: Shared login/logout page

---

## 6. Templates & UI

### 6.1 Template Structure

```
templates/
├── base.html                          # Base layout with navbar
├── home.html                          # Homepage
├── admin/
│   └── base_site.html                 # Custom admin branding
├── auth/
│   └── login-logout.html              # Login/logout page
├── base/
│   ├── hero.html                      # Hero section (unused)
│   ├── navbar.html                    # Navigation bar
│   └── js.html                        # JavaScript includes
├── courses/
│   ├── list.html                      # Course list (full page)
│   ├── detail.html                    # Course detail
│   ├── lesson.html                    # Lesson with video
│   ├── lesson-coming-soon.html        # Coming soon placeholder
│   ├── email-required.html            # Email gate
│   └── snippets/
│       └── list-display.html          # Course list (HTMX snippet)
├── emails/
│   └── hx/
│       ├── form.html                  # Email form (HTMX)
│       └── logout-btn.html            # Logout button (HTMX)
└── videos/
    └── snippets/
        └── embed.html                 # Cloudinary Video Player embed
```

### 6.2 Key Templates

#### Base Template
**File**: `templates/base.html`
- Includes TailwindCSS, Flowbite, DaisyUI
- HTMX script
- Navbar with login/logout state
- Messages framework display

#### Course List
**File**: `templates/courses/list.html`
- Grid layout of course cards
- Cloudinary thumbnails
- Course title, description
- Link to course detail

#### Lesson Detail
**File**: `templates/courses/lesson.html`
- Cloudinary Video Player
- Lesson title, description
- Navigation to other lessons

#### Email Form (HTMX)
**File**: `templates/emails/hx/form.html`
- Email input field
- Submit via HTMX POST
- Success message display
- Conditional rendering (hide if logged in)

### 6.3 UI Components

**Framework**: TailwindCSS v4 + Flowbite + DaisyUI

**Components Used**:
- Navbar (Flowbite)
- Cards (TailwindCSS)
- Forms (TailwindCSS + DaisyUI)
- Buttons (DaisyUI)
- Alerts/Messages (DaisyUI)
- Video Player (Cloudinary)

**Responsive Design**: Mobile-first with TailwindCSS breakpoints

---

## 7. Configuration Files

### 7.1 Django Settings

**File**: [`home/settings.py`](file:///home/mhmd/Desktop/projects/coursehub-django/home/settings.py)

**Key Configurations**:

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Email
EMAIL_HOST = config("EMAIL_HOST")  # smtp.gmail.com
EMAIL_PORT = config("EMAIL_PORT", default='587')
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True)

# Cloudinary
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_PUBLIC_API_KEY = config("CLOUDINARY_PUBLIC_API_KEY")
CLOUDINARY_SECRET_API_KEY = config("CLOUDINARY_SECRET_API_KEY")

# TailwindCSS
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["0.0.0.0", "127.0.0.1"]

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default='').split(',') if host.strip()]
```

### 7.2 URL Configuration

**File**: [`home/urls.py`](./home/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path("courses/", include("courses.urls")),
    path("", views.home_view),
    path("verify-email/<uuid:token>/", verify_email_token_view),
    path("hx/login/", email_token_login_view),
    path("hx/logout/", logout_btn_hx_view),
    path("login/", views.login_logout_template_view),
    path("logout/", views.login_logout_template_view),
]
```

**File**: [`courses/urls.py`](./courses/urls.py)

```python
urlpatterns = [
    path("<slug:course_id>/lessons/<slug:lesson_id>/", views.lesson_detail_view),
    path("<slug:course_id>/", views.course_detail_view),
    path("", views.course_list_view),
]
```

### 7.3 Requirements

**File**: [`requirements.txt`](.)

```
Django>=5.1,<5.2
pillow
cloudinary
python-decouple
django-htmx
psycopg2
django-tailwind[reload]
gunicorn
```

### 7.4 Admin Configuration

**File**: [`courses/admin.py`](./courses/admin.py)

**Features**:
- Inline lesson editing within course admin
- Cloudinary image/video previews
- Custom display fields
- Read-only `public_id` and `updated` fields
- List filters for status and access

**Customizations**:
```python
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [lessonInline]
    list_display = ['title', 'status', 'access']
    list_filter = ['status', 'access']
    readonly_fields = ['public_id', 'display_image']
```

---

## 8. Implementation Patterns

### 8.1 Service Layer Pattern

**Purpose**: Separate business logic from views

**Example**:
```python
# courses/services.py
def get_course_detail(course_id=None):
    if course_id is None:
        return None
    try:
        return Course.objects.get(
            status=PublishStatus.PUBLISHED,
            public_id=course_id
        )
    except:
        return None

# courses/views.py
def course_detail_view(request, course_id=None):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404
    # ...
```

### 8.2 Helper Functions Pattern

**Purpose**: Reusable utilities across models and views

**Example**:
```python
# courses/models.py
def generate_public_id(instance):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")[:5]
    slug = slugify(title)
    return f"{slug}--{unique_id}"

class Course(models.Model):
    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
```

### 8.3 HTMX Progressive Enhancement

**Pattern**: Detect HTMX requests and return partial templates

**Example**:
```python
def course_list_view(request):
    queryset = services.get_publish_courses()
    template_name = "courses/list.html"
    
    if request.htmx:
        template_name = "courses/snippets/list-display.html"
        queryset = queryset[:3]  # Limit for snippet
    
    return render(request, template_name, {"object_list": queryset})
```

### 8.4 Session-Based Access Control

**Pattern**: Store email ID in session for access control

**Example**:
```python
# Set session on verification
request.session['email_id'] = f"{email_obj.id}"

# Check session in views
email_id_exists = request.session.get('email_id')
if lesson_obj.requires_email and not email_id_exists:
    request.session['next_url'] = request.path
    return render(request, "courses/email-required.html", {})
```

---

## 9. Commit History Summary

### 9.1 Development Phases

**Phase 1: Foundation (Oct 24-27, 2025)**
- Project setup
- Course and Lesson models
- Cloudinary integration
- Admin panel customization

**Phase 2: Video & Services (Oct 29 - Nov 6, 2025)**
- Cloudinary Video Player
- Service layer implementation
- Template rendering
- Database migration to MySQL

**Phase 3: Frontend (Nov 16-27, 2025)**
- TailwindCSS v4 + DaisyUI setup
- HTMX integration
- Email verification system
- Login/logout flows

**Phase 4: Polish (Nov 27 - Dec 1, 2025)**
- Flowbite components
- Thumbnail improvements
- UI refinements

### 9.2 Key Architectural Decisions (from commits)

| Decision | Commit | Rationale |
|----------|--------|-----------|
| MySQL over SQLite | `6f8827a` | Resolve database locking issues |
| Service layer | `951c8f0` | Separate business logic from views |
| Cloudinary helpers | `7002f29` | Decouple media handling from models |
| HTMX integration | `8803a17` | Dynamic UI without JavaScript framework |
| Email-only auth | `185da97` | Low-friction access control |

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Total Commits**: 44  
**Development Period**: Oct 24, 2025 - Dec 1, 2025
