from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Execution, Step, ExecutionStatus, Workflow
from ..schemas import ExecutionOut, StepOut
from ..engine.orchestrator import execute_node
from ..engine.graph import first_node
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/executions", tags=["executions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[ExecutionOut])
def list_execs(workflow_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Execution)
    if workflow_id:
        q = q.filter(Execution.workflow_id == workflow_id)
    return q.order_by(Execution.created_at.desc()).limit(100).all()

@router.get("/{exec_id}", response_model=ExecutionOut)
def get_exec(exec_id: str, db: Session = Depends(get_db)):
    ex = db.query(Execution).filter(Execution.id == exec_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")
    return ex

@router.get("/{exec_id}/steps", response_model=list[StepOut])
def get_steps(exec_id: str, db: Session = Depends(get_db)):
    return db.query(Step).filter(Step.execution_id == exec_id).all()

class StartExecutionRequest(BaseModel):
    workflow_id: str
    payload: Dict[str, Any] = {}

@router.post("", response_model=ExecutionOut)
def start_exec(req: StartExecutionRequest, db: Session = Depends(get_db)):
    # validate workflow exists
    wf = db.query(Workflow).filter(Workflow.id == req.workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")

    # create execution entry
    exec_id = str(uuid.uuid4())
    ex = Execution(
        id=exec_id,
        workflow_id=req.workflow_id,
        status=ExecutionStatus.PENDING,
        created_at=datetime.utcnow(),
        context=req.payload or {},
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)

    # find start node and enqueue first task
    start = first_node(wf.definition or {})
    if not start:
        ex.status = ExecutionStatus.FAILED
        db.commit()
        raise HTTPException(400, "Workflow graph has no start node")

    execute_node.delay(exec_id, start)
    return ex
