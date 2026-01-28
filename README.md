# ProSync
### Hybrid Social Collaboration Platform for Developers
**A Modern REST API for GitHub + Instagram-style Collaboration**

## Overview
ProSync is a sophisticated backend API solution that merges the technical collaboration of **GitHub** with the social engagement of **Instagram**. Built with Python and Django, it allows developers to showcase their projects, upload source code (ZIP), collaborate on repos, and build a social following—all within a single mobile-first ecosystem.

## What Problem Does It Solve?
ProSync addresses the challenges of:
* **Fragmented Portfolio Management** - Combining code repos with visual social updates.
* **Complex Collaboration Workflows** - Simplified invite-based team management.
* **Developer Networking** - Follow-based community building specifically for coders.
* **Storage Hurdles** - Automated cloud storage for project assets and profile media.

## Project Information
| Field | Value |
| :--- | :--- |
| **Project Name** | ProSync (Social-Collaboration-Project) |
| **Version** | 1.0.0 |
| **License** | MIT |
| **Type** | RESTful API |
| **Status** | Production Ready |

## Key Features
### Authentication & User Management
* **Token-Based Auth** - Secure session management for Flutter/Mobile apps.
* **Dynamic Profiles** - Expertise tracking (e.g., "Expert in Flutter"), bios, and avatars.
* **Follower System** - Real-time "Follow/Unfollow" logic with notification triggers.

### Hybrid Collaboration Features (GitHub + Instagram)
* **Project Management** - Shared repositories with descriptions, technologies, and tags.
* **Source Code Hosting** - Full support for **Project ZIP uploads** and downloads.
* **Collaborator Roles** - Invite system to add "Lead" or "Contributor" roles to projects.
* **Visual Posts** - Instagram-style project showreels with full "Like" and "Comment" systems.

### Developer & Admin Features
* **Interactive API Documentation** - Built-in **Swagger UI** and **Redoc**.
* **Global Search** - Search projects by technology (e.g., Python) or users by profession.
* **Universal Notifications** - Real-time alerts for likes, follows, and project invites.

## Technology Stack
### Backend Framework
* **Language**: Python 3.10+
* **Framework**: Django 5.2.10
* **API Toolkit**: Django REST Framework (DRF)
* **Architecture**: RESTful API with Serializers

### Database & Storage
* **Local Database**: SQLite
* **Production Database**: PostgreSQL (configured for Render)
* **Storage**: Cloudinary (Persistent Cloud Storage for ZIPs and Images)
* **Static Assets**: Whitenoise (Static file serving)

### Security
* **Authentication**: `rest_framework.authtoken`
* **CORS**: `django-cors-headers` (configured for Flutter integration)
* **Environment**: `python-dotenv` for secret management

## Quick Start
### Prerequisites
* Python 3.10 or higher
* Pip (Package Manager)
* Cloudinary Account (for media hosting)

### Installation Steps
1. **Clone the Project**
   ```bash
   git clone <your-repo-url>
   cd Social/prozync
   ```
2. **Setup Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   CLOUDINARY_CLOUD_NAME=your_name
   CLOUDINARY_API_KEY=your_key
   CLOUDINARY_API_SECRET=your_secret
   ```
5. **Run Migrations & Seed**
   ```bash
   python manage.py migrate
   python seed_data.py
   ```
6. **Start Server**
   ```bash
   python manage.py runserver
   ```

## API Reference
### Base URLs
* **Production**: `https://prozync.onrender.com/`
* **Documentation**: `https://prozync.onrender.com/docs/swagger/`

### Core Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/auth/signup/` | Register a new developer |
| **POST** | `/api/auth/signin/` | User login (returns Token + User Info) |
| **POST** | `/api/auth/forgot-password/` | Request password reset OTP |
| **POST** | `/api/auth/reset-password/` | Reset password using OTP |
| **GET** | `/api/projects/` | List all projects (filtered by tech/trending) |
| **POST** | `/api/projects/` | Create project + Upload ZIP |
| **GET** | `/api/posts/` | List all social posts |
| **POST** | `/api/posts/` | Create post + Upload Image |
| **POST** | `/api/projects/<id>/star/` | Like/Star a repository |
| **POST** | `/api/profiles/<id>/follow/` | Follow a specific developer |
| **GET** | `/api/notifications/` | View likes, follows, and collab invites |

## Database Schema (ProSync Enterprise)
* **User**: Base authentication.
* **Profile**: 1:1 with User. Stores bio, expertise, and avatar.
* **Project**: Owned by User. Contains `project_zip`, technology, and visibility.
* **Post**: Social updates related to projects.
* **Collaboration**: Links Users to Projects with specific Roles.
* **Notification**: Tracks interaction status (Pending/Accepted/Rejected).

## Deployment (Render)
The project is "Render-Ready" with the following files included:
* `build.sh`: Automated install and migration script.
* `Procfile`: Gunicorn setup.
* `settings.py`: Production-ready with PostgreSQL support.

---
**ProSync - Empowering Developer Collaboration**
Made with ❤️ for the Modern Developer Community
