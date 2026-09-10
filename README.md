# Experiment Tracker API

A REST API for organizing and tracking experiments and their runs.

The API will store information about projects, experiments, run parameters, results, and numeric metrics.

## V1

The initial version will have three main resources:

* **Projects** contain experiments.
* **Experiments** belong to projects and contain runs.
* **Runs** store parameters and numeric metrics for an experiment.

V1 will support creating, reading, updating, and deleting these resources, as well as filtering runs.

Authentication, tags, and frontend functionality are outside the initial V1 scope.

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* pytest
* Docker

## Development

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

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```
