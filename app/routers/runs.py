from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Float, cast

from app.database import get_db
from app.models import Experiment, Run
from app.schemas import (
    RunCreate,
    RunResponse,
    RunUpdate,
    RunStatus
)

from app.dependencies import get_experiment_or_404, get_run_or_404

router = APIRouter(tags=["runs"])

@router.post(
    "/experiments/{experiment_id}/runs",
    status_code=201,
    response_model=RunResponse,
)
def create_run(
    experiment_id: int,
    run: RunCreate,
    db: Session = Depends(get_db),
):
    get_experiment_or_404(experiment_id, db)

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

@router.get(
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
    get_experiment_or_404(experiment_id, db)

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

@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = get_run_or_404(run_id, db)

    return run

@router.patch("/runs/{run_id}", response_model=RunResponse)
def patch_run(
    run_id: int,
    run_patch: RunUpdate,
    db: Session = Depends(get_db),
):
    run = get_run_or_404(run_id, db)

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

@router.delete("/runs/{run_id}")
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = get_run_or_404(run_id, db)

    db.delete(run)
    db.commit()

    return {"message": "Run deleted"}