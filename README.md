# Experiment Tracker API

A REST API for organizing and tracking experiments and their runs.

The API stores projects, experiments, run parameters, statuses, and numeric metrics.

## V1

The initial version has three main resources:

- **Projects** contain experiments.
- **Experiments** belong to projects and contain runs.
- **Runs** store parameters, status, numeric metrics, and creation time.

V1 supports:

- CRUD operations for projects, experiments, and runs
- Run filtering by status
- Run filtering by numeric metric threshold
- PostgreSQL persistence
- Database migrations with Alembic
- Automated API tests with pytest
- Docker and Docker Compose development setup

Authentication, tags, and frontend functionality are outside the initial V1 scope.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- pytest
- Docker
- Docker Compose

## Running with Docker

The easiest way to run the project is with Docker Compose.

Build and start the API and PostgreSQL:

```bash
docker compose up --build
```

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation is available at:

http://127.0.0.1:8000/docs

Stop the containers:

```bash
docker compose down
```

To also remove the PostgreSQL data volume and start with a fresh database:

```bash
docker compose down -v
```

Alembic migrations are applied automatically when the API container starts.

## Local Development

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project and its dependencies:

```bash
pip install -e .
```

Create a `.env` file in the project root with a PostgreSQL connection URL:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost/experiment_tracker
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

## Testing

The test suite uses a separate PostgreSQL test database.

Add a test database URL to `.env`:

```env
TEST_DATABASE_URL=postgresql+psycopg://username:password@localhost/experiment_tracker_test
```

Run the tests with:

```bash
pytest -v
```

## API Structure

The main resource hierarchy is:

```text
Project
└── Experiment
    └── Run
```

### Projects

```text
POST   /projects
GET    /projects
GET    /projects/{project_id}
PATCH  /projects/{project_id}
DELETE /projects/{project_id}
```

### Experiments

```text
POST   /projects/{project_id}/experiments
GET    /projects/{project_id}/experiments
GET    /projects/{project_id}/experiments/{experiment_id}
PATCH  /projects/{project_id}/experiments/{experiment_id}
DELETE /projects/{project_id}/experiments/{experiment_id}
```

### Runs

```text
POST   /experiments/{experiment_id}/runs
GET    /experiments/{experiment_id}/runs

GET    /runs/{run_id}
PATCH  /runs/{run_id}
DELETE /runs/{run_id}
```

## Run Filtering

Runs can be filtered by status:

```text
GET /experiments/1/runs?status=completed
```

Supported statuses are:

```text
pending
running
completed
failed
```

Runs can also be filtered by a numeric metric threshold:

```text
GET /experiments/1/runs?metric_name=accuracy&min_metric=0.9
```

The `metric_name` and `min_metric` parameters must be provided together.

Filters can also be combined:

```text
GET /experiments/1/runs?status=completed&metric_name=accuracy&min_metric=0.9
```

## Database Migrations

Database schema changes are managed with Alembic.

After changing SQLAlchemy models, create a migration:

```bash
alembic revision --autogenerate -m "describe migration"
```

Review the generated migration, then apply it:

```bash
alembic upgrade head
```

## Project Structure

```text
app/
├── routers/
│   ├── experiments.py
│   ├── projects.py
│   └── runs.py
├── database.py
├── dependencies.py
├── main.py
├── models.py
└── schemas.py

alembic/
tests/
Dockerfile
compose.yaml
pyproject.toml
```

## V1 Non-Goals

The following are intentionally outside the initial V1 scope:

- Authentication
- Users and permissions
- Tags
- Frontend
- Background workers
- Caching
- Redis

The API is deployment-ready and was successfully deployed with Railway and managed PostgreSQL during V1 development