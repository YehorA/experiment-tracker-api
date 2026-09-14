from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

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