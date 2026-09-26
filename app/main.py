from fastapi import FastAPI

from app.routers import experiments, projects, runs

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Experiment Tracker API"}

app.include_router(projects.router)
app.include_router(experiments.router)
app.include_router(runs.router)