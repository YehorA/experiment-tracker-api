from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.dependencies import get_project_or_404

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", status_code=201, response_model=ProjectResponse)
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


@router.get("", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    db.delete(project)
    db.commit()

    return {"message": "Project deleted"}


@router.patch("/{project_id}", response_model=ProjectResponse)
def patch_project(
    project_id: int,
    project_patch: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

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