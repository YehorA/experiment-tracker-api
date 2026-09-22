from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Float, cast
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Literal

from app.database import get_db
from app.models import Project, Experiment, Run

from pydantic import BaseModel, Field

app = FastAPI()

RunStatus = Literal["pending", "running", "completed", "failed"]


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# --------------------------------------------------------------


class ExperimentCreate(BaseModel):
    name: str
    description: str | None = None


class ExperimentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None = None

class ExperimentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# --------------------------------------------------------------

class RunCreate(BaseModel):
    status: RunStatus = "pending"
    parameters: dict[str, object] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)


class RunResponse(BaseModel):
    id: int
    experiment_id: int
    status: str
    parameters: dict[str, object]
    metrics: dict[str, float]
    created_at: datetime

class RunUpdate(BaseModel):
    status: RunStatus | None = None
    parameters: dict[str, object] | None = None
    metrics: dict[str, float] | None = None

# --------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Experiment Tracker API"}


@app.post("/projects", status_code=201, response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):

    new_project = Project(
        name=project.name,
        description=project.description,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@app.get("/projects", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted"}


@app.patch("/projects/{project_id}", response_model=ProjectResponse)
def patch_project(
    project_id: int,
    project_patch: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if "name" in project_patch.model_fields_set and project_patch.name is None:
        raise HTTPException(
            status_code=422,
            detail="Project name cannot be null",
        )

    updates = project_patch.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        setattr(project, field_name, value)

    db.commit()
    db.refresh(project)

    return project


# --------------------------------------------------------------


@app.post(
    "/projects/{project_id}/experiments",
    status_code=201,
    response_model=ExperimentResponse,
)
def create_experiment(
    project_id: int,
    experiment: ExperimentCreate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    new_experiment = Experiment(
        project_id=project_id,
        name=experiment.name,
        description=experiment.description,
    )

    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)

    return new_experiment


@app.get(
    "/projects/{project_id}/experiments",
    response_model=list[ExperimentResponse],
)
def get_experiments(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(Experiment).filter(Experiment.project_id == project_id).all()


@app.get(
    "/projects/{project_id}/experiments/{experiment_id}",
    response_model=ExperimentResponse,
)
def get_experiment(project_id: int, experiment_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    experiment = (
        db.query(Experiment)
        .filter(
            Experiment.id == experiment_id,
            Experiment.project_id == project_id,
        )
        .first()
    )

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return experiment


@app.patch(
    "/projects/{project_id}/experiments/{experiment_id}",
    response_model=ExperimentResponse,
)
def patch_experiment(
    project_id: int,
    experiment_id: int,
    experiment_patch: ExperimentUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    experiment = (
        db.query(Experiment)
        .filter(
            Experiment.id == experiment_id,
            Experiment.project_id == project_id,
        )
        .first()
    )
    
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if "name" in experiment_patch.model_fields_set and experiment_patch.name is None:
        raise HTTPException(
            status_code=422,
            detail="Experiment name cannot be null",
        )

    updates = experiment_patch.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        setattr(experiment, field_name, value)

    db.commit()
    db.refresh(experiment)

    return experiment

@app.delete("/projects/{project_id}/experiments/{experiment_id}")
def delete_experiment(
    project_id: int,
    experiment_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    experiment = (
            db.query(Experiment)
            .filter(
                Experiment.id == experiment_id,
                Experiment.project_id == project_id,
            )
            .first()
        )
        
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    db.delete(experiment)
    db.commit()

    return {"message": "Experiment deleted"}

# --------------------------------------------------------------

@app.post(
    "/experiments/{experiment_id}/runs",
    status_code=201,
    response_model=RunResponse,
)
def create_run(
    experiment_id: int,
    run: RunCreate,
    db: Session = Depends(get_db),
):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    new_run = Run(
        experiment_id=experiment_id,
        status=run.status,
        parameters=run.parameters,
        metrics=run.metrics,
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    return new_run

@app.get(
    "/experiments/{experiment_id}/runs",
    response_model=list[RunResponse],
)
def get_runs(
    experiment_id: int,
    status: RunStatus | None = None,
    metric_name: str | None = None,
    min_metric: float | None = None,
    db: Session = Depends(get_db),
):
    experiment = (
        db.query(Experiment)
        .filter(Experiment.id == experiment_id)
        .first()
    )

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if (metric_name is None) != (min_metric is None):
        raise HTTPException(
            status_code=422,
            detail="metric_name and min_metric must be provided together",
        )

    query = db.query(Run).filter(Run.experiment_id == experiment_id)

    if status is not None:
        query = query.filter(Run.status == status)

    if metric_name is not None and min_metric is not None:
        query = query.filter(
            cast(Run.metrics[metric_name].astext, Float) >= min_metric
        )

    return query.all()

@app.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return run

@app.patch("/runs/{run_id}", response_model=RunResponse)
def patch_run(
    run_id: int,
    run_patch: RunUpdate,
    db: Session = Depends(get_db),
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    for field_name in ("status", "parameters", "metrics"):
        if (
            field_name in run_patch.model_fields_set
            and getattr(run_patch, field_name) is None
        ):
            raise HTTPException(
                status_code=422,
                detail=f"{field_name} cannot be null",
            )

    updates = run_patch.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        setattr(run, field_name, value)

    db.commit()
    db.refresh(run)

    return run

@app.delete("/runs/{run_id}")
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    db.delete(run)
    db.commit()

    return {"message": "Run deleted"}