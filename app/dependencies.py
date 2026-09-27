from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Experiment, Project, Run


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


def get_experiment_or_404(experiment_id: int, db: Session) -> Experiment:
    experiment = (
        db.query(Experiment)
        .filter(Experiment.id == experiment_id)
        .first()
    )

    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return experiment


def get_project_experiment_or_404(
    project_id: int,
    experiment_id: int,
    db: Session,
) -> Experiment:
    get_project_or_404(project_id, db)

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


def get_run_or_404(run_id: int, db: Session) -> Run:
    run = db.query(Run).filter(Run.id == run_id).first()

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return run