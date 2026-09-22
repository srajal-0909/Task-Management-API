# Task Management REST API

> **Django · Django REST Framework · PostgreSQL · Stateless JWT · Docker · Pytest**

A production-grade, secure Task Management REST API built with Python, Django REST Framework, and PostgreSQL. Features user-scoped CRUD isolation, fine-grained Role-Based Access Control (RBAC), stateless JWT authentication protocols, query filtering, pagination envelopes, and a test suite in Pytest.

---

## Key Highlights

- **Task Tracking Engine**: Secure user-scoped CRUD operations for tasks, categories, and tags with real-time lifecycle tracking (auto-completion syncing & timestamps).
- **Custom Query Filtering**: Powered by `django-filter` supporting status, priority, overdue detection, date intervals (`due_before`, `due_after`, `created_after`), category/tag slugs, and keyword search.
- **Dataset Pagination**: Structured pagination envelope (`count`, `total_pages`, `current_page`, `page_size`, `next`, `previous`, `results`) with dynamic `page_size` query overrides.
- **Stateless JWT Security**: Stateless authentication with SimpleJWT, token pair issuance (access + refresh), claims inside token payloads, and role-based permissions (`ADMIN`, `MANAGER`, `MEMBER`).
- **Containerized DevOps**: Multi-container Docker & Docker Compose setup with PostgreSQL 16 health checks and volume persistence.
- **Automated Pytest Suite**: Complete test coverage across data models, serialization schemas, JWT authentication, user-scoped permissions, query filtering, and pagination.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 5.x & Django REST Framework (DRF) |
| **Authentication** | Stateless JSON Web Tokens (`djangorestframework-simplejwt`) |
| **Database** | PostgreSQL 16 (production/Docker), SQLite (development/testing) |
| **Filtering & Pagination** | `django-filter`, DRF SearchFilter, OrderingFilter, PageNumberPagination |
| **API Docs & Schema** | OpenAPI 3.0 / Swagger UI / Redoc via `drf-spectacular` |
| **Containerization** | Docker & Docker Compose |
| **Testing Engine** | `pytest`, `pytest-django` |

---

## Quickstart with Docker Compose

1. **Clone the repository and prepare environment variables**:
   ```bash
   cp .env.example .env
   ```

2. **Build and start services via Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Apply database migrations & create superuser** (in another terminal):
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application**:
   - API Root: `http://localhost:8000/api/v1/`
   - Swagger UI: `http://localhost:8000/api/docs/swagger/`
   - ReDoc UI: `http://localhost:8000/api/docs/redoc/`

---

## Local Setup (Without Docker)

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**:
   ```bash
   python manage.py makemigrations accounts tasks
   python manage.py migrate
   ```

4. **Start the local development server**:
   ```bash
   python manage.py runserver
   ```

---

## Running Automated Tests

Run the full Pytest automation suite:
```bash
pytest
```

Run with detailed test logs and coverage summary:
```bash
pytest -v -s
```

---

## API Endpoints Reference

### Authentication (`/api/v1/auth/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register/` | Register new user & receive JWT tokens | No |
| `POST` | `/api/v1/auth/login/` | Obtain JWT access + refresh tokens | No |
| `POST` | `/api/v1/auth/refresh/` | Refresh expired access token | No |
| `GET` | `/api/v1/auth/me/` | Retrieve current user profile | Yes |
| `PUT/PATCH`| `/api/v1/auth/me/` | Update current user profile | Yes |
| `POST` | `/api/v1/auth/change-password/` | Change account password | Yes |
| `GET` | `/api/v1/auth/users/` | List users for task assignment | Yes |

### Task Management (`/api/v1/tasks/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/tasks/` | List user-scoped tasks with filters & pagination | Yes |
| `POST` | `/api/v1/tasks/` | Create new task (auto assigns owner) | Yes |
| `GET` | `/api/v1/tasks/{id}/` | Retrieve task details | Yes |
| `PUT/PATCH`| `/api/v1/tasks/{id}/` | Update task details | Yes |
| `DELETE` | `/api/v1/tasks/{id}/` | Delete task (Owner / Admin only) | Yes |
| `POST` | `/api/v1/tasks/{id}/complete/` | Mark task status as `COMPLETED` | Yes |
| `PATCH` | `/api/v1/tasks/{id}/update-status/` | Quick status transition | Yes |
| `GET` | `/api/v1/tasks/summary/` | Aggregate metrics (overdue, priority, status) | Yes |

### Categories & Tags (`/api/v1/categories/`, `/api/v1/tags/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` / `POST` | `/api/v1/categories/` | List & Create user-scoped categories | Yes |
| `GET` / `POST` | `/api/v1/tags/` | List & Create reusable metadata tags | Yes |

---

## Custom Filtering & Query Parameters

The `/api/v1/tasks/` endpoint supports extensive query parameters:

- **Filter by Status**: `?status=TODO` / `?status=IN_PROGRESS` / `?status=COMPLETED`
- **Filter by Priority**: `?priority=CRITICAL` / `?priority=HIGH`
- **Filter by Overdue**: `?is_overdue=true`
- **Date Range Lookups**: `?due_after=2026-09-01&due_before=2026-09-30`
- **Search Query**: `?search=database` (searches title, description, category, and tags)
- **Ordering**: `?ordering=-due_date` / `?ordering=priority` / `?ordering=-created_at`
- **Pagination**: `?page=2&page_size=25`

---

## Role-Based Access Control (RBAC) Matrix

| Role | Own Tasks | Assigned Tasks | Team Tasks | Admin Oversight |
|---|---|---|---|---|
| **MEMBER** | Full CRUD | View & Update Status | No access | No access |
| **MANAGER** | Full CRUD | Full CRUD | Full Read / Update | No access |
| **ADMIN** | Full CRUD | Full CRUD | Full CRUD | Full Access |
#   T a s k - M a n a g e m e n t - A P I 
 
 
