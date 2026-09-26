from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Experiment, Project
from app.schemas import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentUpdate,
)

router = APIRouter(prefix="/projects/{project_id}/experiments", tags=["experiments"])

@router.post("",
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


@router.get("",
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


@router.get("/{experiment_id}",
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


@router.patch("/{experiment_id}",
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

@router.delete("/{experiment_id}")
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
