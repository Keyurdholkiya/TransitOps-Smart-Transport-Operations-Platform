# TransitOps Backend

Backend API for the **TransitOps Smart Transport Operations Platform**, a centralized system for managing transport and logistics operations.

TransitOps supports:

- Authentication and role-based access control
- Vehicle registry
- Driver and licence compliance
- Trip planning and dispatch
- Maintenance management
- Fuel logs
- Expenses
- Operational dashboards
- Reports and analytics

This directory contains the FastAPI and PostgreSQL backend.

## Technology stack

- Python 3.12
- FastAPI
- Pydantic v2
- Pydantic Settings
- PostgreSQL 17
- SQLAlchemy 2 with synchronous sessions
- Psycopg 3
- Alembic
- Argon2 password hashing through `pwdlib`
- JWT access tokens through PyJWT
- Uvicorn
- Pytest
- HTTPX
- Ruff
- Docker Compose
- `uv` package manager

Synchronous SQLAlchemy is intentionally used to keep the hackathon implementation and debugging process straightforward.

## Current implementation status

### Phase 1: Backend foundation

Phase 1 includes:

- FastAPI application structure
- Versioned `/api/v1` routing
- Secure environment configuration
- PostgreSQL Docker service
- SQLAlchemy engine and session management
- Alembic migration foundation
- Database-aware health endpoint
- Application information endpoint
- Standard application exceptions
- Consistent JSON error responses
- Validation and HTTP exception handlers
- Unhandled exception protection
- CORS configuration
- Trusted-host protection
- Security headers middleware
- Basic structured logging
- UTC time utility
- Reusable timestamp model mixin
- Reusable database-session dependency
- Pytest foundation
- Ruff formatting and linting

### Phase 2: Authentication and RBAC

Phase 2 includes:

- Five TransitOps roles
- SQLAlchemy `Role` and `User` models
- Roles and users migration
- UUID user identifiers
- Unique normalized email addresses
- Argon2 password hashing
- JWT Bearer access tokens
- Token issuer, audience and expiry validation
- Generic login errors
- Disabled-user enforcement
- Current-user endpoint
- Admin user-management routes
- Reusable role-checking dependencies
- Initial role and administrator seed command
- Authentication and RBAC tests
- Password-safe response schemas

## Project structure

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── health.py
│   │           ├── info.py
│   │           └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── exception_handlers.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── time.py
│   │   └── tokens.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── middleware/
│   │   └── security_headers.py
│   ├── models/
│   │   ├── mixins.py
│   │   ├── role.py
│   │   └── user.py
│   ├── repositories/
│   │   ├── role_repository.py
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   ├── scripts/
│   │   └── seed_auth.py
│   └── services/
│       ├── auth_service.py
│       └── user_service.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
├── .env.example
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

## Prerequisites

Install:

- Python 3.12
- `uv`
- Docker Desktop
- Git

Confirm the installations:

```bash
python --version
uv --version
docker --version
git --version
```

## Repository setup

Clone the repository:

```bash
git clone https://github.com/Keyurdholkiya/TransitOps-Smart-Transport-Operations-Platform.git
cd TransitOps-Smart-Transport-Operations-Platform
```

Install backend dependencies:

```bash
cd backend
uv sync
```

If the terminal is already inside `backend`, do not run `cd backend` again.

## PostgreSQL setup

PostgreSQL runs through the root `compose.yaml`.

The Docker database uses:

| Setting                    | Value        |
| -------------------------- | ------------ |
| PostgreSQL version         | 17           |
| Host                       | `127.0.0.1`  |
| Host port                  | `5433`       |
| Container port             | `5432`       |
| Database                   | `transitops` |
| User                       | `transitops` |
| Local development password | `transitops` |

Port `5433` is used because a locally installed PostgreSQL server may already occupy port `5432`.

From the repository root, start the Docker services:

```bash
docker compose up -d
```

Check their status:

```bash
docker compose ps
```

The pgAdmin password is unrelated to the TransitOps application database password.

## Environment configuration

From `backend`, copy the environment template.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Bash:

```bash
cp .env.example .env
```

The private `.env` file should contain settings similar to:

```dotenv
APP_NAME=TransitOps API
APP_DESCRIPTION=Backend API for the TransitOps Smart Transport Operations Platform.
APP_VERSION=0.2.0
APP_ENV=local
APP_DEBUG=true

API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://transitops:transitops@127.0.0.1:5433/transitops

SECRET_KEY=replace-with-a-long-random-secret-at-least-32-characters

JWT_ALGORITHM=HS256
JWT_ISSUER=transitops-api
JWT_AUDIENCE=transitops-web
ACCESS_TOKEN_EXPIRE_MINUTES=30

INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_PASSWORD=replace-with-a-strong-unique-password
INITIAL_ADMIN_FULL_NAME=TransitOps Administrator

ALLOWED_ORIGINS=["http://localhost:5173"]

LOG_LEVEL=INFO
ALLOWED_HOSTS=["localhost","127.0.0.1","testserver"]
```

Never commit:

- `backend/.env`
- `backend/.venv/`
- Real passwords
- JWT secrets
- Access tokens

Generate a strong development secret:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into the private `.env` file as `SECRET_KEY`.

## Database connection verification

From `backend`, run:

```bash
uv run python -c "from app.db.session import check_database_connection; check_database_connection(); print('Connected')"
```

Expected result:

```text
Connected
```

If it fails, verify:

- Docker Desktop is running.
- The PostgreSQL container is healthy.
- Port `5433` is used in `DATABASE_URL`.
- The application database credentials match `compose.yaml`.
- The command is being run from `backend`.

## Database migrations

Check the current migration:

```bash
uv run alembic current
```

Check the latest available migration:

```bash
uv run alembic heads
```

Apply all migrations:

```bash
uv run alembic upgrade head
```

Check that SQLAlchemy models match PostgreSQL:

```bash
uv run alembic check
```

Expected result:

```text
No new upgrade operations detected.
```

The Phase 2 migration head is:

```text
aaea2ffdd897
```

### Creating future migrations

Only create a migration after making a real SQLAlchemy model change:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
```

Always inspect the generated migration before applying it.

Do not run migration-generation commands merely as examples. Every generated migration becomes part of the schema history unless deliberately removed before committing.

## Initial authentication seed

After configuring the private initial-admin settings, run:

```bash
uv run python -m app.scripts.seed_auth
```

This creates or updates the five TransitOps roles and creates the initial admin when it does not already exist.

The seed is idempotent:

```bash
uv run python -m app.scripts.seed_auth
```

Running it again does not create duplicate roles or administrators. It also does not overwrite the password of an existing administrator.

## Running the backend

From `backend`, run:

```bash
uv run uvicorn app.main:app --reload
```

The backend is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Request flow

A typical request moves through the backend as follows:

```text
Client request
    ↓
Trusted-host and CORS middleware
    ↓
Security headers middleware
    ↓
FastAPI route
    ↓
Authentication and role dependencies
    ↓
Service layer
    ↓
Repository layer
    ↓
SQLAlchemy session
    ↓
PostgreSQL
    ↓
JSON response
```

Responsibilities are separated as follows:

- Routes handle HTTP input and output.
- Dependencies handle database sessions, authentication and RBAC.
- Services handle business logic and transactions.
- Repositories handle database queries.
- Models describe PostgreSQL tables.
- Schemas validate API input and output.

## Phase 1 API endpoints

| Method | Endpoint         | Description                     |
| ------ | ---------------- | ------------------------------- |
| GET    | `/api/v1/health` | Application and database health |
| GET    | `/api/v1/info`   | Application metadata            |
| GET    | `/docs`          | Swagger UI                      |
| GET    | `/redoc`         | ReDoc documentation             |

The health endpoint returns HTTP `503` when PostgreSQL is unavailable.

## Authentication endpoints

| Method | Endpoint                  | Access        | Description                          |
| ------ | ------------------------- | ------------- | ------------------------------------ |
| POST   | `/api/v1/auth/login`      | Public        | Authenticate with email and password |
| GET    | `/api/v1/auth/me`         | Authenticated | Return the current user              |
| POST   | `/api/v1/users`           | Admin         | Create a user                        |
| GET    | `/api/v1/users`           | Admin         | List users                           |
| GET    | `/api/v1/users/{user_id}` | Admin         | Retrieve a user                      |
| PATCH  | `/api/v1/users/{user_id}` | Admin         | Update a user                        |

## Login request

Send JSON to:

```text
POST /api/v1/auth/login
```

Request body:

```json
{
  "email": "admin@example.com",
  "password": "your-private-password"
}
```

Successful response:

```json
{
  "access_token": "<jwt-access-token>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Use the token on protected endpoints:

```http
Authorization: Bearer <jwt-access-token>
```

Never log or commit the token.

## Current-user response

Request:

```text
GET /api/v1/auth/me
```

Example response:

```json
{
  "email": "admin@example.com",
  "full_name": "TransitOps Administrator",
  "id": "00000000-0000-0000-0000-000000000000",
  "is_active": true,
  "role": {
    "id": 1,
    "name": "admin",
    "display_name": "Admin",
    "description": "Full access, including user and role management."
  },
  "created_at": "2026-07-12T00:00:00Z",
  "updated_at": "2026-07-12T00:00:00Z"
}
```

Password hashes are never included in API responses.

## TransitOps roles

| Role              | Stored value        | Permissions                                            |
| ----------------- | ------------------- | ------------------------------------------------------ |
| Admin             | `admin`             | Full access and user management                        |
| Fleet Manager     | `fleet_manager`     | Vehicles, trips, maintenance and operational dashboard |
| Dispatcher        | `dispatcher`        | View vehicles and drivers; manage dispatch operations  |
| Safety Officer    | `safety_officer`    | Drivers, licences and safety information               |
| Financial Analyst | `financial_analyst` | Fuel, expenses and financial reports                   |

Admin automatically passes all backend role checks.

The frontend may hide controls based on a user’s role, but frontend checks are not security controls. Every protected operation must also enforce authorization in the backend.

## Authentication security

TransitOps authentication provides:

- Argon2 password hashing
- Random password salts
- JWT signature validation
- Fixed HS256 algorithm validation
- Issuer validation
- Audience validation
- Issued-at and expiry claims
- Bearer token protection
- Generic invalid-login responses
- Timing protection for nonexistent users
- Disabled-user checks during login
- Disabled-user checks on every protected request
- Backend role enforcement
- Unique normalized email addresses
- Password-safe response schemas

Unknown email addresses, incorrect passwords and disabled accounts return the same login error:

```json
{
  "error": {
    "code": "invalid_credentials",
    "message": "Invalid email or password.",
    "details": null
  }
}
```

This prevents the login API from revealing whether an email address exists.

## Standard error format

TransitOps errors use:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable message.",
    "details": null
  }
}
```

Common status codes:

| Status | Meaning                                   |
| ------ | ----------------------------------------- |
| 400    | Invalid request or role                   |
| 401    | Missing or invalid authentication         |
| 403    | Authenticated but insufficient permission |
| 404    | Resource not found                        |
| 409    | Unique-value conflict                     |
| 422    | Request validation failed                 |
| 500    | Unexpected server error                   |
| 503    | Database unavailable                      |

## Security headers

Responses include security headers such as:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- Restricted browser permissions policy

Production responses can also include HTTP Strict Transport Security.

## Frontend integration

The frontend integration flow is:

1. Send email and password as JSON to `/api/v1/auth/login`.
2. Receive the JWT access token.
3. Send the token as `Authorization: Bearer <token>`.
4. Call `/api/v1/auth/me` to load the current user and role.
5. Redirect to login when the backend returns `401`.
6. Show an access-denied message for `403`.
7. Never rely only on hidden frontend buttons for security.
8. Never log tokens or passwords.

For production, token storage and transport must be reviewed carefully. The application must use HTTPS.

## Code quality

Format the backend:

```bash
uv run ruff format app tests migrations/env.py
```

Check lint rules:

```bash
uv run ruff check app tests migrations/env.py
```

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Compile Python files:

```bash
uv run python -m compileall app tests
```

Check migrations:

```bash
uv run alembic current
uv run alembic check
```

Complete verification:

```bash
uv run ruff format app tests migrations/env.py
uv run ruff check app tests migrations/env.py
uv run pytest
uv run python -m compileall app tests
uv run alembic current
uv run alembic check
git diff --check
git status
```

## Git workflow

Branches:

- `main`: stable and deployable
- `dev`: shared integration branch
- `feat/*`: individual feature branches

Backend work must not be pushed directly to `main` or `dev`.

Phase 2 branch:

```text
feat/auth-rbac
```

Feature workflow:

```bash
git switch dev
git pull --ff-only origin dev
git switch -c feat/example-feature
git push -u origin feat/example-feature
```

After implementation:

```bash
git status
git add <specific-files>
git commit -m "feat(scope): describe the change"
git push
```

Create a pull request:

```text
feat/example-feature → dev
```

Before merging, confirm:

- Working tree is clean.
- Ruff passes.
- Tests pass.
- Python compilation passes.
- Alembic is at the expected head.
- Alembic detects no missing migrations.
- No `.env`, password, JWT or virtual-environment files are committed.

## Common troubleshooting

### `cd backend` says the path does not exist

The terminal is probably already inside `backend`. Check:

```bash
pwd
```

or in PowerShell:

```powershell
Get-Location
```

### Database connection fails

Check:

```bash
docker compose ps
```

Confirm that `DATABASE_URL` uses host port `5433`, not `5432`.

### Login always returns 401

Check:

- Migrations were applied.
- The seed command ran successfully.
- The email is correct.
- The private admin password matches `.env`.
- The user is active.

Run:

```bash
uv run python -m app.scripts.seed_auth
```

The seed command does not reset an existing admin password.

### Alembic reports new upgrade operations

A model change exists without a migration. Review the changed models and create a real migration:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
```

Inspect the migration before applying it.

### Ruff reports import-order errors

Run:

```bash
uv run ruff check app tests migrations/env.py --fix
uv run ruff format app tests migrations/env.py
```

`--fix` belongs to `ruff check`, not `ruff format`.

## Upcoming phases

Later phases will add:

- Vehicles
- Drivers
- Driver licence compliance
- Trips and dispatching
- Maintenance logs
- Fuel logs
- Expenses
- Dashboard KPIs
- Reports and analytics

## Phase 3: Fleet and Driver Management

Phase 3 introduces the core vehicle and driver management functionality required
for transport operations and future trip dispatching.

### Vehicle management

TransitOps supports:

- Creating vehicles
- Listing and filtering vehicles
- Retrieving individual vehicles
- Updating vehicle information
- Updating operational status
- Unique normalized registration numbers
- Vehicle type and cargo capacity
- Odometer tracking
- Available, On Trip, In Shop and Retired statuses

A retired vehicle cannot return to service. Vehicles can enter On Trip status only
through the future trip dispatch workflow.

### Driver management

TransitOps supports:

- Creating drivers
- Listing and filtering drivers
- Retrieving individual drivers
- Updating driver and licence information
- Updating driver status
- Unique employee codes
- Unique licence numbers
- Optional unique email addresses
- Licence-expiry tracking
- Available, On Trip, Suspended and Inactive statuses

Drivers with expired licences cannot be marked as available or dispatched.
Suspended and inactive drivers cannot be dispatched.

### Phase 3 API endpoints

| Method | Endpoint                               | Purpose                  |
| ------ | -------------------------------------- | ------------------------ |
| POST   | `/api/v1/vehicles`                     | Create a vehicle         |
| GET    | `/api/v1/vehicles`                     | List and filter vehicles |
| GET    | `/api/v1/vehicles/{vehicle_id}`        | Retrieve a vehicle       |
| PATCH  | `/api/v1/vehicles/{vehicle_id}`        | Update a vehicle         |
| PATCH  | `/api/v1/vehicles/{vehicle_id}/status` | Change vehicle status    |
| POST   | `/api/v1/drivers`                      | Create a driver          |
| GET    | `/api/v1/drivers`                      | List and filter drivers  |
| GET    | `/api/v1/drivers/{driver_id}`          | Retrieve a driver        |
| PATCH  | `/api/v1/drivers/{driver_id}`          | Update a driver          |
| PATCH  | `/api/v1/drivers/{driver_id}/status`   | Change driver status     |

### Phase 3 authorization

- Admin users automatically pass all role checks.
- Fleet Managers manage vehicles.
- Safety Officers manage drivers and licence compliance.
- Dispatchers can view vehicles and drivers.
- Vehicle and driver status transitions are validated by the backend.

### Database migration

Phase 3 creates the `vehicles` and `drivers` tables.

Apply migrations with:

```powershell
uv run alembic upgrade head
```
