# System Design Document
## CourseHub Django Platform

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  Browser (HTMX + TailwindCSS + Flowbite + DaisyUI)             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEB SERVER LAYER                             │
│  Django 5.1 (WSGI) + django-htmx Middleware                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   courses    │  │    emails    │  │     home     │
│  (App Layer) │  │  (App Layer) │  │  (App Layer) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └─────────────────┼──────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│  • Course Services  • Email Services  • Cloudinary Helpers      │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  Cloudinary  │  │   Session    │
│   Database   │  │  (CDN/Media) │  │    Store     │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Architecture Pattern**: Layered Monolith with Service Layer  
**Communication**: Synchronous HTTP (HTMX for partial page updates)  
**State Management**: Server-side sessions (Django session framework)

---

## 2. Backend Architecture

### 2.1 Django Application Structure

```
coursehub-django/
├── home/              # Core Django project (settings, root URLs)
├── courses/           # Course & Lesson management
├── emails/            # Email verification system
├── helpers/           # Shared utilities (Cloudinary integration)
├── theme/             # TailwindCSS compilation app
└── templates/         # Global HTML templates
```

### 2.2 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 5.1.x |
| Database | PostgreSQL | 14+ |
| Frontend | HTMX + TailwindCSS v4 + DaisyUI | Latest |
| Media CDN | Cloudinary | Latest |
| Email | SMTP (Gmail) | - |
| Session | Django Sessions (DB-backed) | - |

### 2.3 Installed Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'courses',          # Course/Lesson models
    'emails',           # Email verification
    'django_htmx',      # HTMX integration
    'tailwind',         # TailwindCSS integration
    'theme',            # Custom Tailwind theme
]
```

### 2.4 Middleware Stack

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',  # HTMX request detection
]
```

---

## 3. Module Interactions

### 3.1 Course Module Flow

```
User Request → course_list_view
                    ↓
              get_publish_courses() [service]
                    ↓
              Course.objects.filter(status=PUBLISHED)
                    ↓
              Template: courses/list.html (or HTMX snippet)
                    ↓
              Response with course thumbnails (Cloudinary URLs)
```

### 3.2 Lesson Access Flow

```
User Request → lesson_detail_view
                    ↓
              get_lesson_detail() [service]
                    ↓
         Check: lesson.requires_email?
                    ↓
         ┌──────────┴──────────┐
         ▼                     ▼
    email_id in session?    No email required
         │                     │
    ┌────┴────┐               │
    ▼         ▼               ▼
  Yes        No          Render lesson
    │         │               │
    │    Redirect to      Check video
    │    email form       availability
    │         │               │
    └─────────┴───────────────┘
                    ↓
         Render appropriate template:
         • lesson.html (video available)
         • lesson-coming-soon.html (no video)
```

### 3.3 Email Verification Flow

```
User submits email → EmailForm validation
                           ↓
                  start_verification_event()
                           ↓
              Email.objects.get_or_create(email)
                           ↓
              EmailVerificationEvent.objects.create()
                           ↓
              send_verification_email() [async-ready]
                           ↓
              User clicks link → verify_email_token_view
                           ↓
              verify_token() [service]
                           ↓
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
    Token valid?                        Token invalid?
         │                                   │
    Update attempts                     Return error
    Set session['email_id']             Clear session
         │                                   │
    Redirect to next_url                Redirect to /login/
```

---

## 4. Request Lifecycle

### 4.1 Standard HTTP Request

```
1. Browser → Django WSGI
2. SecurityMiddleware (HTTPS redirect, headers)
3. SessionMiddleware (load session from DB)
4. CSRFMiddleware (validate CSRF token)
5. AuthenticationMiddleware (attach user object)
6. HtmxMiddleware (detect HTMX requests)
7. URL Routing (home.urls → app.urls)
8. View Function
   ├─ Service Layer (business logic)
   ├─ Model Layer (ORM queries)
   └─ Helper Layer (Cloudinary, utilities)
9. Template Rendering
10. Response → Browser
```

### 4.2 HTMX Request (Partial Update)

```
1. HTMX triggers request (hx-get, hx-post)
2. HtmxMiddleware sets request.htmx = True
3. View detects HTMX:
   if request.htmx:
       template_name = "snippet.html"  # Partial template
4. Return HTML fragment (not full page)
5. HTMX swaps fragment into DOM
```

**Example**: Course list on homepage
- Full page: `templates/courses/list.html`
- HTMX snippet: `templates/courses/snippets/list-display.html`

---

## 5. Authentication & Authorization

### 5.1 Email-Based Session Authentication

**No traditional user accounts** — uses email verification for temporary access.

```
┌─────────────────────────────────────────────────────────────┐
│ Email Verification System                                   │
├─────────────────────────────────────────────────────────────┤
│ 1. User submits email via EmailForm                        │
│ 2. Email model: stores unique emails (active/inactive)     │
│ 3. EmailVerificationEvent: generates UUID token & 6-digit OTP
│ 4. Token & OTP sent via email (SMTP)                       │
│ 5. User choice:                                             │
│    a) Click link: /verify-email/<uuid>/                     │
│    b) Enter 6-digit OTP manually                           │
│ 6. Validation:                                              │
│    • Check expired flag (and rate limits)                   │
│    • Check attempts < max_attempts (5)                      │
│    • Update attempts counter                                │
│ 7. On success:                                              │
│    • Set session['email_id'] = email_obj.id                │
│    • Invalidate ALL active codes for this user             │
│    • Redirect to next_url (or /)                           │
│ 8. Session persists until logout or expiry                 │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Access Control Levels

**Course.access** field (AccessRequirement enum):

| Value | Description | Implementation |
|-------|-------------|----------------|
| `any` | Public access | No checks |
| `email` | Email required | Check `session['email_id']` |

**Lesson.can_preview** field:
- `True`: Viewable without email (even if course requires email)
- `False`: Follows course access rules

### 5.3 Authorization Flow

```python
# In lesson_detail_view
email_id_exists = request.session.get('email_id')

if lesson_obj.requires_email and not email_id_exists:
    request.session['next_url'] = request.path
    return render(request, "courses/email-required.html", {})
```

**Session Management**:
- Login: Set `session['email_id']`
- Logout: Delete `session['email_id']` via HTMX POST
- Redirect: Store `session['next_url']` for post-login redirect

---

## 6. Database Design

### 6.1 Schema Overview

```
┌─────────────────┐       ┌─────────────────┐
│     Course      │       │      Email      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ title           │       │ email (UNIQUE)  │
│ public_id       │◄──┐   │ active          │
│ description     │   │   │ timestamp       │
│ image (Cloud.)  │   │   └─────────────────┘
│ access          │   │            │
│ status          │   │            │ FK (parent)
│ timestamp       │   │            ▼
│ updated         │   │   ┌─────────────────────────┐
└─────────────────┘   │   │ EmailVerificationEvent  │
         │            │   ├─────────────────────────┤
         │ 1:N        │   │ id (PK)                 │
         ▼            │   │ parent (FK → Email)     │
┌─────────────────┐   │   │ email                   │
│     Lesson      │   │   │ token (UUID)            │
├─────────────────┤   │   │ attempts                │
│ id (PK)         │   │   │ last_attempt_at         │
│ course (FK) ────┼───┘   │ expired                 │
│ public_id       │       │ expired_at              │
│ title           │       │ timestamp               │
│ description     │       └─────────────────────────┘
│ thumbnail       │
│ video (Cloud.)  │
│ can_preview     │
│ status          │
│ order           │
│ timestamp       │
│ updated         │
└─────────────────┘
```

### 6.2 Model Definitions

#### Course Model

```python
class Course(models.Model):
    title = models.CharField(max_length=120)
    public_id = models.CharField(max_length=130, db_index=True)  # Slug-based
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField("image", tags=["course", "thumbnail"])
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
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
```

**Indexes**: `public_id` (for URL lookups)  
**Cloudinary Integration**: Auto-generates public_id prefix for organized storage

#### Lesson Model

```python
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    public_id = models.CharField(max_length=130, db_index=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    thumbnail = CloudinaryField("image", tags=["thumbnail", "lesson"])
    video = CloudinaryField(
        "video",
        type='private',  # Signed URLs for security
        resource_type='video',
        tags=['video', 'lesson']
    )
    can_preview = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED
    )
    order = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-updated']
```

**Indexes**: `public_id`, `course` (FK auto-indexed)  
**Ordering**: By `order` field, then most recently updated

#### Email Models

```python
class Email(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class EmailVerificationEvent(models.Model):
    parent = models.ForeignKey(Email, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid1)
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    expired = models.BooleanField(default=False)
    expired_at = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Token Security**: UUID v1 (time-based), single-use with attempt limits

### 6.3 Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

**Migration History**: Switched from SQLite to MySQL (commit `6f8827a`) to resolve database locking issues.

---

## 7. Storage Layers & Media Handling

### 7.1 Cloudinary Integration

**Purpose**: Offload media storage and delivery to Cloudinary CDN

```
┌─────────────────────────────────────────────────────────────┐
│ Cloudinary Architecture                                     │
├─────────────────────────────────────────────────────────────┤
│ Django Models (CloudinaryField)                             │
│         ↓                                                    │
│ helpers/_cloudinary/services.py                             │
│         ↓                                                    │
│ Cloudinary Python SDK                                       │
│         ↓                                                    │
│ Cloudinary API (cloud_name, api_key, api_secret)           │
│         ↓                                                    │
│ CDN Delivery (optimized images/videos)                     │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Cloudinary Configuration

```python
# home/settings.py
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_PUBLIC_API_KEY = config("CLOUDINARY_PUBLIC_API_KEY")
CLOUDINARY_SECRET_API_KEY = config("CLOUDINARY_SECRET_API_KEY")

# helpers/_cloudinary/config.py
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_PUBLIC_API_KEY,
    api_secret=CLOUDINARY_SECRET_API_KEY,
    secure=True
)
```

### 7.3 Media Types

| Media Type | Field | Storage Type | Security |
|------------|-------|--------------|----------|
| Course Images | `Course.image` | Public | Unsigned URLs |
| Lesson Thumbnails | `Lesson.thumbnail` | Public | Unsigned URLs |
| Lesson Videos | `Lesson.video` | **Private** | **Signed URLs** |

**Video Security**: Private videos use signed URLs with expiration to prevent unauthorized access.

### 7.4 Cloudinary Helpers

#### Image Helper

```python
def get_cloudinary_image_object(
    instance, 
    field_name="image",
    as_html=False,
    width=1200,
    format=None
):
    # Returns URL or HTML <img> tag
    # Supports dynamic transformations (width, format)
```

**Use Cases**:
- Course thumbnails (382px width)
- Lesson thumbnails (382px width, auto-generated from video if missing)
- Admin previews (200px width)

#### Video Helper

```python
def get_cloudinary_video_object(
    instance,
    field_name="video",
    as_html=False,
    width=None,
    height=None,
    sign_url=True,  # Private videos
    fetch_format="auto",
    quality="auto",
    controls=True,
    autoplay=True
):
    # Returns signed URL or Cloudinary Video Player embed
```

**Video Player**: Uses Cloudinary Video Player (JavaScript) for adaptive streaming, quality selection, and analytics.

### 7.5 Public ID Generation

```python
def generate_public_id(instance):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")[:5]
    slug = slugify(title)
    return f"{slug}--{unique_id}"

def get_public_id_prefix(instance):
    # Organizes uploads by model:
    # course/<public_id>/image.jpg
    # lesson/<public_id>/video.mp4
    model_name_slug = slugify(instance.__class__.__name__)
    return f"{model_name_slug}/{instance.public_id}"
```

**Benefits**:
- Human-readable URLs
- Organized folder structure in Cloudinary
- Collision-free with UUID suffix

---

## 8. Performance Considerations

### 8.1 Database Optimization

| Strategy | Implementation |
|----------|----------------|
| Indexes | `public_id` fields (db_index=True) for URL lookups |
| Query Optimization | Service layer uses `filter()` with specific fields |
| Foreign Key Indexes | Auto-indexed by Django (course_id in Lesson) |
| Ordering | `Lesson.Meta.ordering` for consistent results |

### 8.2 Caching Strategy

**Current**: No caching layer (suitable for MVP)

**Future Recommendations**:
- Redis for session storage (faster than DB)
- Cloudinary CDN (already implemented for media)
- Django template fragment caching for course lists
- Database query caching for published courses

### 8.3 HTMX Performance Benefits

- **Reduced Payload**: Only HTML fragments sent (not full pages)
- **No SPA Overhead**: No JavaScript framework bundle
- **Progressive Enhancement**: Works without JavaScript
- **Server-Side Rendering**: Fast initial page load

### 8.4 Cloudinary Optimizations

```python
# Automatic optimizations
fetch_format="auto"  # Serves WebP/AVIF to supported browsers
quality="auto"       # Adaptive quality based on content
```

**Video Streaming**: Adaptive bitrate streaming (HLS/DASH) via Cloudinary Player

---

## 9. Deployment Architecture

### 9.1 Production Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Internet                                                    │
│      ↓                                                       │
│  [Reverse Proxy: Nginx/Caddy]                               │
│      ↓                                                       │
│  [WSGI Server: Gunicorn/uWSGI]                              │
│      ↓                                                       │
│  [Django Application]                                        │
│      ↓                                                       │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ PostgreSQL DB│  Cloudinary  │  SMTP Server │            │
│  └──────────────┴──────────────┴──────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Environment Configuration

**Required Environment Variables**:

```bash
# Django Core
SECRET_KEY=your-secret-key-here-use-secrets-token-urlsafe-50
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=Database_name_here
DB_USER=database_user_here
DB_PASSWORD=secure_password_here
DB_PORT=5432
DB_HOST=localhost
# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_PUBLIC_API_KEY=your_api_key
CLOUDINARY_SECRET_API_KEY=your_api_secret

# Email (SMTP)
EMAIL_ADDRESS=noreply@yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Admin
ADMIN_USER_NAME=Admin Name
ADMIN_USER_EMAIL="YOUR_ADMIN_USER_EMAIL"
```

### 9.3 Static Files

**Development**:
```python
STATIC_URL = 'static/'
# Served by Django runserver
```

**Production**:
```bash
python manage.py collectstatic
# Serve via Nginx/Caddy (not Django)
```

**TailwindCSS Compilation**:
```bash
# Development
python manage.py tailwind start

# Production
python manage.py tailwind build
```

### 9.4 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (use secrets.token_urlsafe(50))
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enforced (SecurityMiddleware)
- [ ] CSRF protection enabled
- [ ] Cloudinary signed URLs for private videos
- [ ] Database credentials in environment variables
- [ ] Email verification token expiration
- [ ] Rate limiting on email sending (future)

### 9.5 Deployment Steps

1. **Prepare Environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Compile Static Assets**
   ```bash
   python manage.py tailwind build
   python manage.py collectstatic --noinput
   ```

4. **Run WSGI Server**
   ```bash
   gunicorn home.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Configure Reverse Proxy** (Nginx example)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location /static/ {
           alias /path/to/static/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 10. Design Decisions & Rationale

### 10.1 Why HTMX?

- **Simplicity**: No complex JavaScript framework
- **Server-Side Logic**: Business logic stays in Python
- **Progressive Enhancement**: Works without JS
- **Small Bundle**: ~14KB (vs React ~100KB+)

### 10.2 Why Email-Only Auth?

- **Low Friction**: No password management
- **Temporary Access**: Suitable for course previews
- **Future-Proof**: Can add full user accounts later

### 10.3 Why Cloudinary?

- **Scalability**: No server storage limits
- **Performance**: Global CDN delivery
- **Video Streaming**: Adaptive bitrate out-of-the-box
- **Transformations**: On-the-fly image resizing

### 10.4 Why PostgreSQL over SQLite?

- **Concurrency**: No database locking issues
- **Production-Ready**: Better for multi-user scenarios
- **Scalability**: Handles larger datasets
- **Advanced Features**: Full-text search, JSON support, better indexing

---

## 11. Future Enhancements

### 11.1 Planned Features

- **User Accounts**: Full authentication system
- **Payment Integration**: Stripe/PayPal for paid courses
- **Progress Tracking**: Lesson completion tracking
- **Comments**: Lesson-level discussions
- **Certificates**: Course completion certificates

### 11.2 Technical Improvements

- **Caching**: Redis for sessions and queries
- **Background Tasks**: Celery for email sending
- **Rate Limiting**: Prevent email spam
- **Analytics**: Track lesson views and engagement
- **Search**: Full-text search for courses/lessons

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Project Status**: Production-Ready MVP
