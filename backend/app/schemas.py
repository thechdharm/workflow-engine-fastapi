from pydantic import BaseModel, Field
from typing import Any, Optional, List

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    definition: dict = Field(default_factory=dict)
    trigger: dict = Field(default_factory=dict)
    graph: dict = Field(default_factory=dict)
    is_active: bool = True

class WorkflowOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    version: int
    is_active: bool
    trigger: dict
    graph: dict
    class Config:
        from_attributes = True

class ExecutionOut(BaseModel):
    id: str
    workflow_id: str
    status: str
    context: Optional[dict] = None
    class Config:
        from_attributes = True

class StepOut(BaseModel):
    id: str
    execution_id: str
    node_id: str
    type: str
    status: str
    output: Optional[dict] = None
    error: Optional[dict] = None
    class Config:
        from_attributes = True
