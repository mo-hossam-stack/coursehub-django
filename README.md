# 🎓 Django HTMX Course Platform

A modern **course management platform** built with **Django 5**, **HTMX**, and **TailwindCSS**, featuring dynamic course access control, short-lived email verification, and clean UI interactions without heavy JavaScript frameworks.

---

## 🧰 Tech Stack

| Layer | Technology |
|--------|-------------|
| Backend | [Django 5.1](https://www.djangoproject.com/) |
| Language | [Python 3.12](https://www.python.org/) |
| Frontend | [HTMX](https://htmx.org) + [Flowbite](https://flowbite.com) + [TailwindCSS](https://tailwindcss.com) |
| Integration | [django-htmx](https://github.com/adamchainz/django-htmx), [django-tailwind](https://django-tailwind.readthedocs.io/) |
| Media Storage | [Cloudinary](https://cloudinary.com/documentation/django_integration) |

---

## 📖 Overview

This project implements a **full-featured course platform** that supports:

### 🧩 Courses
- Title, Description, and Thumbnail  
- Access Levels:
  - `Anyone`
  - `Email Required`
  - `Purchase Required`
  - `User Required` *(n/a for now)*
- Status:
  - `Published`
  - `Coming Soon`
  - `Draft`
- Lessons:
  - Title, Description, Video, and Status
#curr working on
### ✉️ Email Verification Flow
Short-lived email verification system for temporary access:
- Collect user email
- Send verification token
- Validate token and activate session

Models:
- `Email`
- `EmailVerificationToken`

---