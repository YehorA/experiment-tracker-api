from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

projects = []

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

@app.get("/")
def root():
    return {"message": "Experiment Tracker API"}

@app.post("/projects", status_code=201)
def create_project(project: ProjectCreate):
    new_project = {
        "id": len(projects) + 1,
        "name": project.name,
        "description": project.description
    }

    projects.append(new_project)
    return new_project

@app.get("/projects")
def get_projects():
    return projects

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    for project in projects:
        if project["id"] == project_id:
            return project

    raise HTTPException(status_code=404, detail="Project not found")