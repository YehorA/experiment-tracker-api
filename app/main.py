from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
projects = []
next_project_id = 1

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
def create_project(project: ProjectCreate):
    global next_project_id

    new_project = {
        "id": next_project_id,
        "name": project.name,
        "description": project.description
    }

    next_project_id += 1
    projects.append(new_project)
    return new_project

@app.get("/projects", response_model=list[ProjectResponse])
def get_projects():
    return projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    for project in projects:
        if project["id"] == project_id:
            return project

    raise HTTPException(status_code=404, detail="Project not found")

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    for project in projects:
        if project["id"] == project_id:
            projects.remove(project)
            return {"message": "Project deleted"}

    raise HTTPException(status_code=404, detail="Project not found")

@app.patch("/projects/{project_id}", response_model=ProjectResponse)
def patch_project(project_id: int, project_patch: ProjectUpdate):
    for project in projects:
        if project["id"] == project_id:
            if "name" in project_patch.model_fields_set and project_patch.name is None:
                raise HTTPException(
                    status_code=422,
                    detail="Project name cannot be null"
    )
            updates = project_patch.model_dump(exclude_unset=True)
            project.update(updates)
            return project

    raise HTTPException(status_code=404, detail="Project not found")