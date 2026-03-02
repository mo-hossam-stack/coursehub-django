<p align="center">
  <img src="https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django 5.1" />
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/HTMX-Latest-3D72D7?style=for-the-badge&logo=htmx&logoColor=white" alt="HTMX" />
  <img src="https://img.shields.io/badge/TailwindCSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="TailwindCSS v4" />
  <img src="https://img.shields.io/badge/PostgreSQL-14+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Cloudinary-CDN-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white" alt="Cloudinary" />
</p>

<h1 align="center">🎓 CourseHub</h1>

<p align="center">
  <strong>A modern, production-ready course management platform</strong><br/>
  Built with <strong>Django 5.1</strong>, <strong>HTMX</strong>, and <strong>TailwindCSS v4</strong> — no heavy JavaScript frameworks required.
</p>

<p align="center">
  <a href="https://www.linkedin.com/posts/mohamed-hossam-dev_backend-systemdesign-django-activity-7406460049235222528-tMwU?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFjEZA8B-prD-yP6Bz7y8xP7CBtDVirxijw">
    🎬 Watch the Video Demo on LinkedIn
  </a>
</p>

---

## 🌐 Overview

**CourseHub** is a full-stack course management platform designed for creators who want to publish video courses with sophisticated access control. The platform features:

- **Zero-password authentication** — users verify via email links or 6-digit OTP codes
- **Cloudinary-powered video streaming** — adaptive bitrate, signed private URLs, responsive thumbnails
- **HTMX-driven interactivity** — SPA-like experience with partial page updates, no React/Vue needed
- **Production-grade infrastructure** — Docker multi-stage builds, Nginx reverse proxy, Gunicorn WSGI, WhiteNoise static serving

> **Philosophy**: Ship fast, stay lightweight. CourseHub proves you don't need a JavaScript framework to build a modern, interactive web application.

---

## Key Features

### Course Management
| Feature | Description |
|---------|-------------|
| **Course Creation** | Title, rich description, thumbnail image, and access control |
| **Video Lessons** | Cloudinary-powered adaptive video streaming with signed URLs |
| **Access Control** | Two levels — `Anyone` (public) or `Email Required` (gated) |
| **Publication Workflow** | Three states — `Published`, `Coming Soon`, `Draft` |
| **SEO-Friendly URLs** | Slug-based public IDs with unique UUID suffixes (e.g., `/courses/python-basics--a1b2c`) |
| **Lesson Ordering** | Configurable display order with automatic sorting |
| **Preview Lessons** | Mark specific lessons as free previews for email-gated courses |

### Passwordless Authentication
| Feature | Description |
|---------|-------------|
| **Email Verification** | UUID-based token links sent via SMTP |
| **6-Digit OTP** | Manual code entry as an alternative to link clicking |
| **Rate Limiting** | Maximum 5 verification attempts per email per hour |
| **Attempt Tracking** | Per-token attempt counting with automatic expiration |
| **Session Management** | Secure session-based access with `email_id` stored in session |
| **Redirect Memory** | `next_url` session storage to redirect users after verification |
| **HTMX Login Flow** | Inline email → OTP form transitions without page reloads |

### User Interface
| Feature | Description |
|---------|-------------|
| **HTMX Partial Updates** | Dynamic content loading without full page refreshes |
| **TailwindCSS v4** | Utility-first CSS with `django-tailwind` integration |
| **Flowbite Components** | Pre-built interactive UI components |
| **DaisyUI** | Extended Tailwind component library |
| **Mobile-First Design** | Fully responsive across all viewports |
| **CSRF Protection** | Automatic CSRF token injection via `hx-headers` on `<body>` |

### Cloudinary Media Pipeline
| Feature | Description |
|---------|-------------|
| **Private Video Storage** | Videos stored as `type='private'` with signed URL access |
| **Adaptive Streaming** | Responsive video breakpoints (320px → 1920px) |
| **Smart Image Optimization** | Auto-format (WebP/AVIF), smart gravity cropping, DPR-aware |
| **Responsive Thumbnails** | `srcset` generation with 5 breakpoints for optimal loading |
| **Video Poster Generation** | Auto-generated poster images from video frames |
| **Blur-Up Placeholders** | Low-quality image placeholders for progressive loading |
| **Mobile-Optimized Video** | Network-quality-aware video delivery (`eco`, `good`, `best`) |

### Admin Panel
| Feature | Description |
|---------|-------------|
| **Inline Lesson Editing** | Stacked inline lessons within course admin |
| **Media Previews** | Live Cloudinary image/video previews directly in admin |
| **List Filters** | Filter courses by status and access level |
| **Auto-Generated IDs** | `public_id` generated automatically from title + UUID |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (Port 80/443)                     │
│                    Reverse Proxy + SSL + Gzip                   │
├─────────────────────────────────────────────────────────────────┤
│                                 │                               │
│                    ┌────────────▼────────────┐                  │
│                    │   Gunicorn WSGI Server  │                  │
│                    │      (Port 8000)        │                  │
│                    └────────────┬────────────┘                  │
│                                 │                               │
│  ┌──────────────────────────────▼──────────────────────────┐    │
│  │                    Django 5.1 Application                │    │
│  │                                                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │    │
│  │  │ courses  │  │  emails  │  │ helpers  │  │  home   │ │    │
│  │  │          │  │          │  │          │  │         │ │    │
│  │  │ Models   │  │ Models   │  │Cloudinary│  │Settings │ │    │
│  │  │ Views    │  │ Views    │  │ Services │  │ URLs    │ │    │
│  │  │ Services │  │ Services │  │ Config   │  │ Views   │ │    │
│  │  │ Admin    │  │ Forms    │  │          │  │         │ │    │
│  │  └────┬─────┘  └────┬─────┘  └──────────┘  └─────────┘ │    │
│  │       │              │                                   │    │
│  │  ┌────▼──────────────▼────┐   ┌───────────────────────┐ │    │
│  │  │   PostgreSQL 14+       │   │   Cloudinary CDN      │ │    │
│  │  │   (Persistent Data)    │   │   (Media Storage)     │ │    │
│  │  └────────────────────────┘   └───────────────────────┘ │    │
│  │                                                          │    │
│  │  ┌────────────────────────┐   ┌───────────────────────┐ │    │
│  │  │ WhiteNoise             │   │ SMTP (Gmail)          │ │    │
│  │  │ (Static File Serving)  │   │ (Email Delivery)      │ │    │
│  │  └────────────────────────┘   └───────────────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```
---

## Getting Started

### Prerequisites

| Requirement | Version | Required For |
|-------------|---------|-------------|
| Python | 3.12+ | Runtime |
| PostgreSQL | 14+ | Database |
| Node.js | Latest LTS | TailwindCSS compilation |
| Cloudinary Account | — | Media storage & streaming |
| Gmail App Password | — | SMTP email delivery |

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/mo-hossam-stack/coursehub-django.git
cd coursehub-django
```

#### 2. Create & Activate Virtual Environment

```bash
pip install uv 
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

#### 3. Install Python Dependencies

```bash
# Using pip
uv pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

#### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values 

#### 5. Set Up PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE coursehub_db;
CREATE USER coursehub_user WITH PASSWORD 'your_secure_password';
ALTER ROLE coursehub_user SET client_encoding TO 'utf8';
ALTER ROLE coursehub_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE coursehub_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE coursehub_db TO coursehub_user;
\q
```

#### 6. Run Database Migrations

```bash
python manage.py migrate
```

#### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

#### 8. Install TailwindCSS Dependencies

```bash
python manage.py tailwind install
```

#### 9. Start Development Servers

You'll need **two terminals** running simultaneously:

```bash
# Terminal 1 — Django development server
python manage.py runserver

# Terminal 2 — TailwindCSS file watcher (hot-reloads CSS)
python manage.py tailwind start
```

#### 10. Access the Application

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Home page |
| `http://localhost:8000/courses/` | Course listing |
| `http://localhost:8000/admin/` | Django admin panel |

---

## Docker Deployment

### Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with production values

# 2. Build and start all services
docker compose up -d --build

# 3. Run database migrations
docker compose exec web python manage.py migrate

# 4. Create admin user
docker compose exec web python manage.py createsuperuser

# 5. Access the application
#    → http://localhost:8000 (via Gunicorn)
#    → http://localhost:80  (via Nginx)
```
### Useful Docker Commands

```bash
# View logs
docker compose logs -f web

# Access Django shell
docker compose exec web python manage.py shell

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes database data)
docker compose down -v
```

### Security Controls

- **Rate Limiting**: Maximum 5 verification emails per email address per hour
- **Attempt Limiting**: Maximum 5 verification attempts per token (auto-expires)
- **Token Expiration**: Tokens marked expired after successful use or max attempts
- **Session Binding**: Verified `email_id` stored in server-side session
- **Open Redirect Protection**: `next_url` validated to start with `/`

---

## Documentation

Detailed documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [`System_Design.md`](docs/System_Design.md) | Full system architecture and design decisions |
| [`Dev_Plan.md`](docs/Dev_Plan.md) | Development roadmap and task planning |
| [`Docker_Setup.md`](docs/Docker_Setup.md) | Comprehensive Docker deployment guide |
| [`Project_Implementation_Reference.md`](docs/Project_Implementation_Reference.md) | Implementation details and code reference |

---


## Contact

**Mohamed Hossam** — [LinkedIn](https://www.linkedin.com/in/mohamed-hossam-dev/) — [GitHub](https://github.com/mo-hossam-stack)

For questions, issues, or feature requests, please [open an issue](https://github.com/mo-hossam-stack/coursehub-django/issues) on GitHub.

---

<p align="center">
  <strong>Built with ❤️ using Django, HTMX, and TailwindCSS</strong>
  <br/><br/>
  <img src="https://img.shields.io/badge/Made%20With-Python-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Powered%20By-Django-092E20?style=flat&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Styled%20With-TailwindCSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white" />
</p>