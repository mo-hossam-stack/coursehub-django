# 🎓 CourseHub - Django HTMX Course Platform

A modern, production-ready **course management platform** built with **Django 5.1**, **HTMX**, and **TailwindCSS v4**. Features passwordless email authentication, Cloudinary video streaming, and a clean, responsive UI without heavy JavaScript frameworks.

[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![HTMX](https://img.shields.io/badge/HTMX-Latest-orange.svg)](https://htmx.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38bdf8.svg)](https://tailwindcss.com)

---
## 📣 Check Out My LinkedIn Post

[🔹 View Video demo on LinkedIn](https://www.linkedin.com/posts/mohamed-hossam-dev_backend-systemdesign-django-activity-7406460049235222528-tMwU?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFjEZA8B-prD-yP6Bz7y8xP7CBtDVirxijw)

## ✨ Features

### 📚 Course Management
- **Course Creation**: Title, description, thumbnail, and access control
- **Video Lessons**: Cloudinary-powered adaptive video streaming
- **Access Control**: Public, email-required, or purchase-required courses
- **Publication Status**: Published, coming soon, or draft
- **SEO-Friendly URLs**: Slug-based URLs with unique identifiers

### 🔐 Authentication
- **Passwordless Email Auth**: UUID-based email verification tokens
- **Secure OTP**: 6-digit verification codes for manual entry
- **Session Management**: Secure session-based access control
- **Email Verification**: SMTP integration with Gmail
- **Access Gates**: Redirect users to email verification when required

### 🎨 User Interface
- **HTMX Dynamic Updates**: Partial page updates without full reloads
- **TailwindCSS v4**: Modern, responsive design
- **Flowbite Components**: Pre-built UI components
- **DaisyUI**: Additional UI utilities
- **Mobile-First**: Fully responsive across all devices

### 🎥 Media Handling
- **Cloudinary CDN**: Scalable media storage and delivery
- **Video Streaming**: Adaptive bitrate streaming with Cloudinary Player
- **Image Optimization**: Automatic format conversion (WebP/AVIF)
- **Thumbnail Generation**: Auto-generate thumbnails from video frames

### ⚙️ Admin Panel
- **Custom Admin**: Enhanced Django admin with inline lesson editing
- **Media Previews**: Cloudinary image/video previews in admin
- **Bulk Management**: Manage courses and lessons efficiently

---

## 🧰 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend** | Django | 5.1.x |
| **Language** | Python | 3.12+ |
| **Database** | PostgreSQL | 14+ |
| **Frontend** | HTMX + TailwindCSS v4 + Flowbite + DaisyUI | Latest |
| **Media CDN** | Cloudinary | Latest |
| **Email** | SMTP (Gmail) | - |
| **Deployment** | Docker + Gunicorn + Nginx | Latest |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Node.js (for TailwindCSS)
- Cloudinary account
- Gmail account (for SMTP)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mo-hossam-stack/coursehub-django.git
   cd coursehub-django
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   sudo -u postgres psql
   CREATE DATABASE coursehub_db;
   CREATE USER coursehub_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE coursehub_db TO coursehub_user;
   \q
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Install TailwindCSS dependencies**
   ```bash
   python manage.py tailwind install
   ```

9. **Start development servers**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver

   # Terminal 2: TailwindCSS watcher
   python manage.py tailwind start
   ```

10. **Access the application**
    - Frontend: http://localhost:8000
    - Admin: http://localhost:8000/admin

---

## 🐳 Docker Deployment

### Quick Start with Docker

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build and start services**
   ```bash
   docker compose up -d --build
   ```

3. **Run migrations**
   ```bash
   docker compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. **Access application**
   - Application: http://localhost:8000
   - Admin: http://localhost:8000/admin

6. **Stop services**
   - docker compose down

### Docker Services

- **db**: PostgreSQL 14 database
- **web**: Django application with Gunicorn
- **nginx**: Reverse proxy (production)

For detailed Docker setup instructions, see [`Docker_Setup.md`](Docker_Setup.md).

---

## 📁 Project Structure

```
coursehub-django/
├── courses/              # Course and Lesson models, views, services
├── emails/               # Email verification system
├── helpers/              # Cloudinary integration utilities
├── home/                 # Django project settings and root URLs
├── templates/            # HTML templates
│   ├── base.html
│   ├── courses/
│   ├── emails/
│   └── auth/
├── theme/                # TailwindCSS compilation app
├── nginx/                # Nginx configuration
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

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
ADMIN_USER_EMAIL="YOUR_ADMIN_USER_EMAIL"```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 📚 Usage

### Creating Courses

1. Access admin panel: http://localhost:8000/admin
2. Navigate to **Courses** → **Add Course**
3. Fill in course details:
   - Title, description
   - Upload thumbnail image
   - Set access level (Anyone, Email Required)
   - Set status (Published, Coming Soon, Draft)
4. Add lessons inline:
   - Title, description
   - Upload video to Cloudinary
   - Set lesson order
   - Mark as preview (optional)

### Email Verification Flow

1. User visits course/lesson requiring email
2. Email form appears (HTMX)
3. User submits email
4. Verification email sent with UUID token and 6-digit OTP
5. User can:
   - Click verification link
   - Enter 6-digit code manually in the new input UI
6. Session enriched with email ID
7. User redirected to requested content

---

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

### TailwindCSS

```bash
# Development (watch mode)
python manage.py tailwind start

# Production build
python manage.py tailwind build
```

---

## 🌐 Production Deployment



   
   ```

For detailed deployment instructions, 
---

## 📊 Database Schema

### Models

- **Course**: Title, description, image, access level, status
- **Lesson**: Title, description, video, thumbnail, order, can_preview
- **Email**: Email address, active status
- **EmailVerificationEvent**: Token, attempts, expiration

### Relationships

- Course → Lessons (1:N)
- Email → EmailVerificationEvent (1:N)

---

## 🔐 Security

- **CSRF Protection**: Enabled on all forms
- **Session Security**: HTTP-only cookies
- **Email Verification**: UUID tokens with attempt limits
- **Private Videos**: Signed Cloudinary URLs
- **SQL Injection**: Django ORM protection
- **XSS Protection**: Template auto-escaping

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---



## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [HTMX](https://htmx.org) - Dynamic HTML updates
- [TailwindCSS](https://tailwindcss.com) - CSS framework
- [Cloudinary](https://cloudinary.com) - Media CDN
- [Flowbite](https://flowbite.com) - UI components
- [DaisyUI](https://daisyui.com) - Tailwind components

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Django, HTMX, and TailwindCSS**