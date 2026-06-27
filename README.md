# Job Service

Job Service owns job categories, job postings, and job lifecycle status for Labora. It serves client job management, freelancer job browsing, internal job verification, and status transitions used by applications, reviews, messaging, and admin workflows.

## Responsibilities

- Let clients create and list their jobs.
- Let freelancers browse open jobs and view job details.
- Manage job lifecycle states: `open`, `in_progress`, `submitted`, `completed`, and `cancelled`.
- Expose internal job details and statistics to other services.
- Send notifications for work submission and job completion.

## Features

- Client-only job creation and own-job listing.
- Freelancer-only open-job browsing with optional `q` title search and pagination.
- Admin-only job deletion.
- Internal status updates used by Application Service.
- Completion workflow that verifies the authenticated client owns the job.

## API Endpoints

Base path: `/api/`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `jobs/create/` | Client JWT | Create a job for the authenticated client. |
| `GET` | `jobs/client/` | Client JWT | List jobs owned by the authenticated client. |
| `GET` | `jobs/browse/` | Freelancer JWT | List open jobs. Supports `q` and `page`. |
| `GET` | `jobs/<job_id>/` | Client, freelancer, or admin JWT | Return job details. |
| `DELETE` | `jobs/delete/<job_id>` | Admin JWT | Delete a job. |
| `PATCH` | `jobs/<job_id>/submit/` | Bearer JWT | Move an `in_progress` job to `submitted` and notify the client. |
| `PATCH` | `jobs/<job_id>/complete/` | Owning client JWT | Move a `submitted` job to `completed` and notify the accepted freelancer when known. |

## Internal Service Endpoints

Internal endpoints use `X-Service-Key: <SERVICE_API_KEY>`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `internal/jobs/<job_id>/` | Return `id`, `client_id`, `freelancer_id` if Application Service resolves it, and `status`. |
| `PATCH` | `internal/jobs/<job_id>/status/` | Update job status. Sends a completion notification when status becomes `completed`. |
| `GET` | `internal/jobs/` | Return paginated job summaries. |
| `GET` | `internal/jobs/stats/` | Return aggregate job counts by status. |

## Authentication

JWT-protected APIs use the shared RS256 public key and role helpers in `job.authentication` / `job.role_permissions`. Internal APIs bypass JWT and require the service key.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key. |
| `DEBUG` | Enables debug mode when set to `true`. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL database configuration. |
| `JWT_PUBLIC_KEY_PATH` | Public key used to verify Auth Service JWTs. |
| `SERVICE_API_KEY` | Shared key for internal endpoints. |
| `APPLICATION_SERVICE_URL` | Used to resolve accepted freelancer information. |
| `NOTIFICATION_SERVICE_URL` | Used by shared notification client / direct notification calls. |
| `*_SERVICE_URL` | Additional service URL settings loaded by the common configuration pattern. |

## Setup

```bash
cd JobService
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8005
```

## Service Architecture

- Django project: `project`
- App: `job`
- Authentication: `job.authentication.CustomJWTAuthentication`
- Internal permission: `job.permissions.internal_service.IsInternalService`
- Outbound dependencies: Application Service and Notification Service

## Database Models

- `Category`: job category name.
- `Job`: stores `client_id`, title, description, category, budget range, deadline, status, and timestamps.

## Notification/Event Flow

- `PATCH jobs/<job_id>/submit/` sends `work_submitted` to the job client.
- Completing a job sends `job_completed` to the accepted freelancer when Application Service returns one.
