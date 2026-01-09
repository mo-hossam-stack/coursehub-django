# Development Plan
## CourseHub Django Platform

Structured development roadmap with implemented features, missing features, refactors, technical debt, and future enhancements.

---

## Phase 1: Foundation ✅ COMPLETE

**Timeline**: Oct 24-27, 2025  
**Status**: ✅ Fully Implemented

### Implemented Features

- [x] Django 5.1 project initialization
- [x] Course model with title, description, status, access control
- [x] Lesson model with title, description, video, thumbnail
- [x] Cloudinary integration for media storage
- [x] Public ID generation (slug + UUID)
- [x] PostgreSQL database configuration
- [x] Admin panel with inline lesson editing
- [x] Cloudinary image/video previews in admin
- [x] Path generation for SEO-friendly URLs

### Key Commits

- `a0d9cfa`: Project setup
- `d27a1c0`: Course model initialization
- `b1a9580`: Cloudinary configuration
- `4c18a7c`: Lesson model initialization
- `a2839f7`: Public ID generation
- `6f8827a`: **Migration from SQLite to PostgreSQL**

### Design Decisions

- **PostgreSQL over SQLite**: Resolved database locking issues for concurrent access and better production scalability
- **Cloudinary**: Offload media storage to CDN for scalability
- **Public ID pattern**: `{slug}--{uuid5}` for human-readable + unique URLs

---

## Phase 2: Video Streaming & Services ✅ COMPLETE

**Timeline**: Oct 29 - Nov 6, 2025  
**Status**: ✅ Fully Implemented

### Implemented Features

- [x] Cloudinary Video Player integration
- [x] Signed URLs for private videos
- [x] Service layer for business logic separation
- [x] Course and lesson detail views
- [x] Template rendering system
- [x] Video player with adaptive streaming
- [x] Thumbnail generation from video frames
- [x] Helper functions for Cloudinary objects

### Key Commits

- `3eef0f7`: Cloudinary video object service
- `75ce3b9`: Cloudinary Video Player integration
- `951c8f0`: Service layer implementation
- `c2b32f0`: Template rendering
- `2cc3e44`: Video player for users

### Technical Improvements

- **Service Layer**: Decoupled business logic from views
- **Helper Module**: Reusable Cloudinary utilities
- **Video Security**: Private videos with signed URLs

---

## Phase 3: Frontend & Authentication ✅ COMPLETE

**Timeline**: Nov 16-27, 2025  
**Status**: ✅ Fully Implemented

### Implemented Features

- [x] TailwindCSS v4 + DaisyUI setup
- [x] HTMX integration for dynamic updates
- [x] Email verification system
- [x] UUID-based verification tokens
- [x] SMTP email sending (Gmail)
- [x] Session-based authentication
- [x] Login/logout flows
- [x] Email-required access control
- [x] HTMX email form
- [x] Logout button (HTMX)

### Key Commits

- `8803a17`: TailwindCSS v4 + DaisyUI + HTMX setup
- `185da97`: Email verification models
- `a2015ef`: Gmail SMTP configuration
- `7db0eab`: UUID verification links
- `bf25dd8`: Token verification service
- `e97333a`: Session enrichment with email ID
- `50fd3aa`: Email-required lesson access
- `48b566b`: HTMX email login form
- `bbd097f`: Logout logic

### Authentication Flow

1. User submits email via HTMX form
2. System generates UUID token
3. Email sent with verification link
4. User clicks link → token validated
5. Session enriched with `email_id`
6. Access granted to email-required content

---

## Phase 4: UI Polish ✅ COMPLETE

**Timeline**: Nov 27 - Dec 1, 2025  
**Status**: ✅ Fully Implemented

### Implemented Features

- [x] Flowbite component integration
- [x] Course list with thumbnails
- [x] Responsive design
- [x] Video frame as lesson thumbnail fallback
- [x] Hero section (removed later)
- [x] Navigation bar with login state

### Key Commits

- `c4d26a6`: Flowbite setup
- `3488947`: Login/logout views and URLs
- `1d40c9e`: Course list with thumbnails
- `0f9e447`: Video frame as lesson thumbnail
- `cc5d228`: Remove hero section icons


---

## Phase 5: OTP & Security Enhancements ✅ COMPLETE

**Timeline**: Dec 29-30, 2025  
**Status**: ✅ Fully Implemented

### Implemented Features

- [x] 6-digit OTP generation and verification
- [x] Rate limiting (backend)
- [x] Resend cooldown timer (frontend)
- [x] Multiple valid OTP support
- [x] Secure OTP invalidation on success
- [x] Improved HTML email templates
- [x] HTMX logic for OTP input UI

### Key Commits

- `Implemented 6-digit input component`
- `Added rate limiting logic`
- `Refined verification service`

---

## Phase 6: Missing Features & Future Enhancements

### 5.1 User Accounts (Not Implemented)

**Priority**: High  
**Effort**: Medium  
**Dependencies**: None

#### Features to Implement

- [ ] User registration with password
- [ ] Django authentication backend
- [ ] User profile model
- [ ] Password reset flow
- [ ] Social authentication (Google, GitHub)
- [ ] User dashboard

#### Implementation Steps

1. Create `User` model extending `AbstractUser`
2. Update `EMAIL_BACKEND` to support user accounts
3. Create registration/login views
4. Update access control to support both email and user auth
5. Add user profile page
6. Implement password reset with email

#### Database Changes

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 5.2 Payment Integration (Not Implemented)

**Priority**: High  
**Effort**: High  
**Dependencies**: User Accounts

#### Features to Implement

- [ ] Stripe/PayPal integration
- [ ] Course pricing model
- [ ] Payment processing
- [ ] Purchase history
- [ ] Invoices/receipts
- [ ] Subscription plans

#### Implementation Steps

1. Add `price` field to `Course` model
2. Create `Purchase` model
3. Integrate Stripe API
4. Create checkout flow
5. Webhook handling for payment events
6. Update access control to check purchases

#### Database Changes

```python
class Course(models.Model):
    # Existing fields...
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=True)

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20)  # pending, completed, refunded
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

### 5.3 Progress Tracking (Not Implemented)

**Priority**: Medium  
**Effort**: Medium  
**Dependencies**: User Accounts

#### Features to Implement

- [ ] Lesson completion tracking
- [ ] Course progress percentage
- [ ] Resume from last watched
- [ ] Progress dashboard
- [ ] Completion certificates

#### Implementation Steps

1. Create `LessonProgress` model
2. Track video watch time
3. Mark lessons as complete
4. Calculate course completion percentage
5. Generate completion certificates (PDF)

#### Database Changes

```python
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    watch_time = models.IntegerField(default=0)  # seconds
    last_watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'lesson')
```

---

### 5.4 Comments & Discussions (Not Implemented)

**Priority**: Medium  
**Effort**: Medium  
**Dependencies**: User Accounts

#### Features to Implement

- [ ] Lesson-level comments
- [ ] Reply threads
- [ ] Upvoting/downvoting
- [ ] Instructor responses
- [ ] Comment moderation

#### Implementation Steps

1. Create `Comment` model
2. Add comment form to lesson template
3. Implement reply threading
4. Add voting system
5. Create moderation dashboard

#### Database Changes

```python
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    is_instructor = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

### 5.5 Search & Filtering (Not Implemented)

**Priority**: Medium  
**Effort**: Low  
**Dependencies**: None

#### Features to Implement

- [ ] Full-text search for courses
- [ ] Filter by category/tags
- [ ] Sort by popularity, date, price
- [ ] Search autocomplete

#### Implementation Steps

1. Add `category` and `tags` fields to `Course`
2. Implement search view with Q objects
3. Add search bar to navbar
4. Create filter UI
5. (Optional) Integrate Elasticsearch for advanced search

#### Database Changes

```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

class Course(models.Model):
    # Existing fields...
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
```

---

### 5.6 Analytics & Reporting (Not Implemented)

**Priority**: Low  
**Effort**: Medium  
**Dependencies**: User Accounts, Progress Tracking

#### Features to Implement

- [ ] Instructor dashboard
- [ ] Course enrollment stats
- [ ] Lesson view counts
- [ ] Revenue reports
- [ ] User engagement metrics

#### Implementation Steps

1. Create `CourseView` model for tracking
2. Implement analytics dashboard
3. Generate charts (Chart.js)
4. Export reports (CSV/PDF)

---

## Phase 7: Refactors & Technical Debt

### 6.1 Code Quality Improvements

**Priority**: Medium  
**Effort**: Low

#### Refactors Needed

- [ ] **Error Handling**: Replace bare `except:` with specific exceptions
  - `courses/services.py`: Lines 17, 43
  - `emails/views.py`: Line 17
  
- [ ] **Type Hints**: Add type annotations to all functions
  ```python
  def get_course_detail(course_id: str | None = None) -> Course | None:
      ...
  ```

- [ ] **Logging**: Replace `print()` statements with proper logging
  - `courses/views.py`: Line 45
  - `home/views.py`: Lines 11, 23, 24
  - `emails/views.py`: Line 43

- [ ] **Constants**: Extract magic numbers to settings
  ```python
  # settings.py
  EMAIL_VERIFICATION_MAX_ATTEMPTS = 5
  COURSE_LIST_HTMX_LIMIT = 3
  ```

- [ ] **Docstrings**: Add docstrings to all public functions and classes

---

### 6.2 Performance Optimizations

**Priority**: Medium  
**Effort**: Medium

#### Optimizations Needed

- [ ] **Database Queries**:
  - Add `select_related('course')` to lesson queries
  - Add `prefetch_related('lesson_set')` to course queries
  - Index `email` field in `Email` model (already unique, but explicit index)

- [ ] **Caching**:
  - Cache published courses list (Redis)
  - Cache Cloudinary URLs (avoid repeated API calls)
  - Template fragment caching for course cards

- [ ] **Cloudinary**:
  - Lazy load images (use `loading="lazy"` attribute)
  - Optimize thumbnail sizes (use responsive images)

---

### 7.3 Security Hardening

**Priority**: High  
**Effort**: Low

#### Security Improvements

- [x] **Rate Limiting**:
  - Limit email verification requests (django-ratelimit custom implementation)
  - Limit login attempts (disabled button)
  
- [x] **Token Expiration**:
  - Add time-based expiration to email tokens (implemented in Services)
  ```python
  # emails/services.py
  # check_rate_limit() and expired check added
  ```

- [ ] **CSRF Exemption Audit**:
  - Ensure all HTMX endpoints have CSRF protection

- [ ] **Content Security Policy**:
  - Add CSP headers for XSS protection

- [ ] **SQL Injection**:
  - Audit all raw queries (none currently, but future-proof)

---

### 6.4 Testing

**Priority**: High  
**Effort**: High

#### Tests to Implement

- [ ] **Unit Tests**:
  - Service layer functions
  - Model methods (`generate_public_id`, `get_thumbnail`)
  - Helper functions (Cloudinary)

- [ ] **Integration Tests**:
  - Email verification flow
  - Course/lesson access control
  - HTMX endpoints

- [ ] **End-to-End Tests**:
  - User journey: Browse → Email → Watch lesson
  - Admin: Create course → Add lessons → Publish

#### Test Structure

```
tests/
├── test_models.py
├── test_services.py
├── test_views.py
├── test_helpers.py
└── test_integration.py
```

---

## Phase 7: Infrastructure & DevOps

### 7.1 Deployment Automation

**Priority**: Medium  
**Effort**: Medium

#### Tasks

- [ ] **Docker Setup** (See Docker_Setup.md)
- [ ] **CI/CD Pipeline**:
  - GitHub Actions for automated testing
  - Automated deployment to staging/production
  
- [ ] **Environment Management**:
  - Separate `.env` files for dev/staging/prod
  - Secret management (AWS Secrets Manager, Vault)

- [ ] **Monitoring**:
  - Sentry for error tracking
  - Prometheus + Grafana for metrics
  - Uptime monitoring (UptimeRobot, Pingdom)

---

### 7.2 Scalability

**Priority**: Low  
**Effort**: High

#### Future Scalability Needs

- [ ] **Database**:
  - Read replicas for high traffic
  - Connection pooling (PgBouncer)
  
- [ ] **Caching**:
  - Redis cluster for distributed caching
  - CDN for static assets (Cloudflare, AWS CloudFront)

- [ ] **Background Jobs**:
  - Celery for async email sending
  - Celery Beat for scheduled tasks (e.g., token cleanup)

- [ ] **Load Balancing**:
  - Multiple Django instances behind load balancer
  - Horizontal scaling with Kubernetes

---

## Phase 8: Content Management

### 8.1 Course Creation Tools

**Priority**: Medium  
**Effort**: Medium

#### Features to Implement

- [ ] **Bulk Upload**:
  - CSV import for courses/lessons
  - Batch video upload to Cloudinary

- [ ] **Rich Text Editor**:
  - Replace plain text descriptions with WYSIWYG editor (TinyMCE, CKEditor)

- [ ] **Course Templates**:
  - Pre-defined course structures
  - Duplicate course functionality

---

### 8.2 Student Engagement

**Priority**: Medium  
**Effort**: Medium

#### Features to Implement

- [ ] **Quizzes**:
  - Lesson-level quizzes
  - Course final exam
  - Auto-grading

- [ ] **Assignments**:
  - File upload for assignments
  - Instructor feedback

- [ ] **Notifications**:
  - Email notifications for new lessons
  - In-app notifications
  - Push notifications (PWA)

---

## Technical Debt Summary

### Critical (Fix Immediately)

1. **Error Handling**: Replace bare `except:` with specific exceptions
2. **Logging**: Replace `print()` with proper logging
3. **Security**: Add rate limiting to email endpoints

### High Priority (Fix Soon)

1. **Testing**: Implement unit and integration tests
2. **Type Hints**: Add type annotations
3. **Token Expiration**: Add time-based expiration to email tokens

### Medium Priority (Fix Later)

1. **Performance**: Add database query optimization
2. **Caching**: Implement Redis caching
3. **Documentation**: Add docstrings to all functions

### Low Priority (Nice to Have)

1. **Code Style**: Enforce with Black, isort, flake8
2. **Pre-commit Hooks**: Automate code quality checks
3. **API Documentation**: Generate OpenAPI/Swagger docs (if API added)

---

## Roadmap Timeline

### Q1 2026: Core Enhancements

- [ ] User accounts and authentication
- [ ] Payment integration (Stripe)
- [ ] Progress tracking
- [ ] Testing suite

### Q2 2026: Engagement Features

- [ ] Comments and discussions
- [ ] Quizzes and assignments
- [ ] Search and filtering
- [ ] Notifications

### Q3 2026: Scalability

- [ ] Redis caching
- [ ] Celery background tasks
- [ ] CI/CD pipeline
- [ ] Monitoring and analytics

### Q4 2026: Advanced Features

- [ ] Mobile app (React Native)
- [ ] Live streaming
- [ ] Certificates
- [ ] Instructor dashboard

---

## Development Best Practices

### For New Developers

1. **Read Documentation First**:
   - System_Design.md for architecture
   - Project_Implementation_Reference.md for implementation details
   - This Dev_Plan.md for roadmap

2. **Follow Patterns**:
   - Use service layer for business logic
   - Use helpers for reusable utilities
   - Use HTMX for dynamic updates

3. **Testing**:
   - Write tests before implementing new features
   - Test both happy path and edge cases

4. **Code Review**:
   - All changes require code review
   - Follow Django best practices
   - Maintain consistency with existing code

5. **Git Workflow**:
   - Feature branches: `feature/user-accounts`
   - Bugfix branches: `fix/email-verification`
   - Commit messages: `feat(courses): add search functionality`

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-09  
**Project Phase**: MVP Complete, Ready for Enhancements
