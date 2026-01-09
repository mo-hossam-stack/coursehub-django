# Docker Setup Guide
## CourseHub Django Platform

Complete Docker configuration for development and production deployment with PostgreSQL.

---

## Table of Contents

1. [Dockerfile (Production-Ready)](#1-dockerfile-production-ready)
2. [docker compose.yml (Full Stack)](#2-docker composeyml-full-stack)
3. [Environment Configuration](#3-environment-configuration)
4. [Build & Run Instructions](#4-build--run-instructions)
5. [Production Deployment](#5-production-deployment)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Dockerfile (Production-Ready)

**File**: `Dockerfile`

```dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build stage for TailwindCSS compilation
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Node.js for TailwindCSS compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install TailwindCSS dependencies and build
RUN python manage.py tailwind install
RUN python manage.py tailwind build

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=home.settings

# Install system dependencies for PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Copy static files from builder
COPY --from=builder --chown=appuser:appuser /app/staticfiles /app/staticfiles

# Create media directory
RUN mkdir -p /app/media && chown appuser:appuser /app/media

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/courses/')"

# Run gunicorn
CMD ["gunicorn", "home.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60"]
```

**Key Features**:
- **Multi-stage build**: Reduces final image size
- **Non-root user**: Security best practice
- **Health check**: Container health monitoring
- **Optimized layers**: Cached dependencies for faster builds
- **PostgreSQL client**: libpq-dev for psycopg2

---

## 2. docker compose.yml (Full Stack)

**File**: `docker compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:14-alpine
    container_name: coursehub_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-coursehub_db}
      POSTGRES_USER: ${DB_USER:-coursehub_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - coursehub_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-coursehub_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django Application
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: coursehub_web
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn home.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    volumes:
      - ./:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      db:
        condition: service_healthy
    networks:
      - coursehub_network

  # Nginx Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    container_name: coursehub_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL certificates
    depends_on:
      - web
    networks:
      - coursehub_network

volumes:
  postgres_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local

networks:
  coursehub_network:
    driver: bridge
```

**Services**:
- **db**: PostgreSQL 14 database
- **web**: Django application with Gunicorn
- **nginx**: Reverse proxy for production

---

## 3. Environment Configuration

### 3.1 .env File Template

**File**: `.env.example`

```bash
# Django Core
SECRET_KEY=your-secret-key-here-use-secrets-token-urlsafe-50
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
BASE_URL=https://yourdomain.com

# Database (PostgreSQL)
DB_NAME=coursehub_db
DB_USER=coursehub_user
DB_PASSWORD=secure_password_here
DB_HOST=db
DB_PORT=5432

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
ADMIN_USER_EMAIL=admin@yourdomain.com
```

**Setup Instructions**:
```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3.2 Nginx Configuration

**File**: `nginx/conf.d/coursehub.conf`

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client body size (for file uploads)
    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (if not using Cloudinary for everything)
    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    # Proxy to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

---

## 4. Build & Run Instructions

### 4.1 Development Setup

**Prerequisites**:
- Docker 20.10+
- Docker Compose 2.0+

**Steps**:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/coursehub-django.git
cd coursehub-django

# 2. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 3. Build images
docker compose build

# 4. Start services
docker compose up -d

# 5. Run migrations
docker compose exec web python manage.py migrate

# 6. Create superuser
docker compose exec web python manage.py createsuperuser

# 7. Access application
# http://localhost:8000
# Admin: http://localhost:8000/admin

# 6.Stop services
  docker compose down
```

### 4.2 Development with Hot Reload

For development with live code reloading:

**File**: `docker compose.dev.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: coursehub_db
      POSTGRES_USER: coursehub_user
      POSTGRES_PASSWORD: devpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./:/app  # Mount source code for hot reload
    ports:
      - "8000:8000"
    env_file:
      - .env.dev
    environment:
      - DEBUG=True
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db

  tailwind:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: python manage.py tailwind start
    volumes:
      - ./:/app
    depends_on:
      - web

volumes:
  postgres_data:
```

**File**: `Dockerfile.dev`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    pkg-config \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**Run Development**:
```bash
docker compose -f docker compose.dev.yml up
```

### 4.3 Common Commands

```bash
# View logs
docker compose logs -f web

# Execute Django commands
docker compose exec web python manage.py <command>

# Access Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes database)
docker compose down -v

# Rebuild after code changes
docker compose up -d --build

# View running containers
docker compose ps
```

---

## 5. Production Deployment

### 5.1 Pre-Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Generate strong `SECRET_KEY`
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure Cloudinary credentials
- [ ] Set up SMTP for email sending
- [ ] Configure database backups
- [ ] Set up monitoring (Sentry, Prometheus)

### 5.2 SSL Certificate Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Set permissions
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
```

**Auto-renewal**:
```bash
# Add to crontab
0 0 1 * * certbot renew --quiet && docker compose restart nginx
```

### 5.3 Production Deployment Steps

```bash
# 1. SSH into production server
ssh user@yourserver.com

# 2. Clone repository
git clone https://github.com/yourusername/coursehub-django.git
cd coursehub-django

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with production values

# 4. Build and start services
docker compose up -d --build

# 5. Run migrations
docker compose exec web python manage.py migrate

# 6. Create superuser
docker compose exec web python manage.py createsuperuser

# 7. Collect static files (already done in Dockerfile, but verify)
docker compose exec web python manage.py collectstatic --noinput

# 8. Verify services
docker compose ps
docker compose logs web

# 9. Access application
# https://yourdomain.com
```

### 5.4 Database Backups

**Automated Backup Script**:

**File**: `scripts/backup_db.sh`

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="coursehub_db_$DATE.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T db pg_dump \
    -U ${DB_USER:-coursehub_user} \
    ${DB_NAME:-coursehub_db} | gzip > $BACKUP_DIR/$BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Job**:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh
```

**Restore Backup**:
```bash
# Restore from backup
gunzip < /backups/postgresql/coursehub_db_20251210_020000.sql.gz | \
docker compose exec -T db psql -U coursehub_user coursehub_db
```

### 5.5 Monitoring & Logging

**Docker Logs**:
```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f web

# View last 100 lines
docker compose logs --tail=100 web
```

**Log Rotation**:

**File**: `/etc/docker/daemon.json`

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Health Checks**:
```bash
# Check container health
docker compose ps

# Check web service health
curl -f http://localhost:8000/courses/ || echo "Service unhealthy"
```

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Database Connection Errors

**Symptom**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
```bash
# Check database container is running
docker compose ps db

# Check database logs
docker compose logs db

# Verify environment variables
docker compose exec web env | grep DB_

# Restart database
docker compose restart db

# Test connection
docker compose exec db psql -U coursehub_user -d coursehub_db -c "SELECT 1;"
```

#### Static Files Not Loading

**Symptom**: CSS/JS files return 404

**Solution**:
```bash
# Rebuild with static files
docker compose exec web python manage.py collectstatic --noinput

# Check static volume
docker volume inspect coursehub-django_static_volume

# Verify nginx configuration
docker compose exec nginx nginx -t

# Restart nginx
docker compose restart nginx
```

#### Permission Errors

**Symptom**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Fix ownership
docker compose exec web chown -R appuser:appuser /app

# Check user
docker compose exec web whoami
```

#### Out of Memory

**Symptom**: Container crashes or freezes

**Solution**:
```bash
# Check resource usage
docker stats

# Increase memory limit in docker compose.yml
services:
  web:
    mem_limit: 2g
    memswap_limit: 2g
```

### 6.2 Performance Tuning

**Gunicorn Workers**:
```bash
# Formula: (2 x CPU cores) + 1
# For 4 cores: 9 workers
CMD ["gunicorn", "home.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "9"]
```

**Database Connection Pooling**:

**File**: `home/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... other settings
        'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
    }
}
```

### 6.3 Debugging

**Enable Debug Mode (Development Only)**:
```bash
# .env.dev
DEBUG=True

# Restart
docker compose -f docker compose.dev.yml up -d
```

**Access Container Shell**:
```bash
# Django container
docker compose exec web bash

# Database container
docker compose exec db sh

# Nginx container
docker compose exec nginx sh
```

**Database Access**:
```bash
# PostgreSQL shell
docker compose exec db psql -U coursehub_user -d coursehub_db

# Run SQL query
docker compose exec db psql -U coursehub_user -d coursehub_db -c "SELECT * FROM courses_course LIMIT 5;"
```

---

## 7. Advanced Configurations

### 7.1 Redis for Caching (Optional)

**Add to docker compose.yml**:

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: coursehub_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - coursehub_network

volumes:
  redis_data:
```

**Django Settings**:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 7.2 Celery for Background Tasks (Optional)

**Add to docker compose.yml**:

```yaml
services:
  celery:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A home worker -l info
    volumes:
      - ./:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis
    networks:
      - coursehub_network

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A home beat -l info
    volumes:
      - ./:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis
    networks:
      - coursehub_network
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Example

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/coursehub-django
            git pull origin main
            docker compose down
            docker compose up -d --build
            docker compose exec -T web python manage.py migrate
            docker compose exec -T web python manage.py collectstatic --noinput
```

---

**Document Version**: 2.0  
**Last Updated**: 2025-12-10  
**Database**: PostgreSQL 14+  
**Docker Version**: 20.10+  
**Docker Compose Version**: 2.0+
