from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Workflow
from ..schemas import WorkflowCreate, WorkflowOut
from ..utils import gen_id

router = APIRouter(prefix="/workflows", tags=["workflows"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=WorkflowOut)
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db)):
    definition = body.definition or body.graph or {}
    wf = Workflow(
        id=gen_id(),
        name=body.name,
        description=body.description,
        definition=definition,
        trigger=body.trigger,
        graph=body.graph or definition,
        is_active=body.is_active,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf

@router.get("", response_model=list[WorkflowOut])
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()

@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    return wf

@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: str, body: WorkflowCreate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    new_definition = body.definition or body.graph or {}
    wf.name = body.name
    wf.description = body.description
    if new_definition:
        wf.definition = new_definition
    wf.trigger = body.trigger
    if body.graph or new_definition:
        wf.graph = body.graph or new_definition
    wf.is_active = body.is_active
    wf.version += 1
    db.commit()
    db.refresh(wf)
    return wf

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    db.delete(wf)
    db.commit()
    return {"status": "deleted"}
