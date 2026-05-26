# Job Service – Freelancing Platform

## Overview

The Job Service is a stateless microservice responsible for managing job postings in the freelancing platform. It allows clients to create jobs, freelancers to browse jobs, and admins to manage job listings.

This service integrates with an external Auth Service using JWT-based authentication.

---

## Architecture

* **Auth Service**

  * Handles user authentication
  * Issues JWT tokens signed with a private key (RS256)

* **Job Service**

  * Verifies JWT tokens using public key
  * Enforces role-based access control
  * Handles job-related operations

* **API Gateway (Nginx)**

  * Routes requests to appropriate services

---

## Features

* Job category management
* Client job posting
* Freelancer job browsing
* Job search and filtering
* Admin job deletion
* Stateless JWT authentication
* Role-based access control

---

## Authentication & Authorization

### JWT Authentication

* All requests require:

  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
* Tokens are verified using **public key (RS256)**

### Token Validation

The service validates:

* Signature
* Expiration (`exp`)
* Issuer (`iss`)
* Audience (`aud`) (optional but recommended)

### Example JWT Payload

```
{
  "user_id": 5,
  "role": "CLIENT"
}
```

---

## Role-Based Access Control

| Endpoint     | Allowed Role |
| ------------ | ------------ |
| Create Job   | CLIENT       |
| View My Jobs | CLIENT       |
| Browse Jobs  | FREELANCER   |
| Delete Job   | ADMIN        |

---

## Ownership Validation

* A client can only access their own jobs
* `client_id` is always extracted from JWT

Example:

```python
if job.client_id != request.auth["user_id"]:
    raise PermissionDenied("Unauthorized access")
```

---

## Request Flow

1. User logs in via Auth Service
2. JWT token is issued
3. Client sends request with token
4. API Gateway routes request
5. Job Service:

   * Verifies JWT
   * Extracts user info
   * Validates role
   * Processes request

---

## Tech Stack

* Backend: Django, Django REST Framework
* Authentication: JWT (RS256)
* Database: SQLite (Dev), PostgreSQL (Prod)
* Tools: Postman, Git, GitHub

---

## Project Structure

```
JobService_labora/

job/
 ├── models.py
 ├── serializers.py
 ├── views.py
 ├── urls.py
 ├── admin.py
 └── authentication.py

JobService/
 ├── settings.py
 └── urls.py

manage.py
```

---

## API Endpoints

### Create Job (Client Only)

```
POST /api/jobs/create/
```

### View My Jobs (Client)

```
GET /api/jobs/my/
```

### Browse Jobs (Freelancer)

```
GET /api/jobs/browse/?q=keyword
```

### Job Detail

```
GET /api/jobs/<job_id>/
```

### Delete Job (Admin Only)

```
DELETE /api/jobs/<job_id>/
```

---

## Security Design

* JWT signature verification (RS256)
* Role-based authorization
* Ownership validation
* Stateless authentication
* No trust on frontend data

---

## Best Practices

* Use HTTPS in production
* Store secrets in `.env`
* Never expose private key
* Log failed authentication attempts
* Validate all input data

---

## Deployment Checklist

* Set `DEBUG=False`
* Use PostgreSQL
* Configure `ALLOWED_HOSTS`
* Enable HTTPS
* Configure CORS
* Use environment variables

---

## Future Improvements

* Rate limiting
* Centralized logging
* API Gateway authentication layer
* Caching (Redis)
* Event-driven communication (Kafka/RabbitMQ)

---

## Conclusion

The Job Service ensures secure and scalable job management by combining stateless authentication, strict authorization, and microservice best practices.

---
