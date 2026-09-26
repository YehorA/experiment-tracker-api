from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

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