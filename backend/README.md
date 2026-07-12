# TransitOps Backend

FastAPI backend for the TransitOps Smart Transport Operations Platform.

## Current Scope

Phase 1 provides:

- FastAPI application structure
- Environment-based configuration
- PostgreSQL database
- SQLAlchemy session management
- Alembic migrations
- Health and application information APIs
- CORS and trusted-host protection
- Security headers
- Standard API error responses
- Structured logging
- Shared timestamp utilities
- Automated tests and code-quality checks

Authentication, RBAC and business entities will be implemented in later phases.

## Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL 17
- SQLAlchemy 2
- Alembic
- Psycopg 3
- Pydantic Settings
- Pytest
- Ruff
- Docker Compose
- uv

## Requirements

Install:

- Python 3.12
- uv
- Docker Desktop

## Local Setup

From the repository root, start PostgreSQL:

```bash
docker compose up -d postgres
```
