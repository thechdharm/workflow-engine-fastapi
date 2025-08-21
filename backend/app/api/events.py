from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Workflow, Execution
from ..utils import gen_id
from ..engine.orchestrator import execute_node
from ..engine.graph import first_node

try:
    from json_logic import jsonLogic
except Exception:
    from jsonlogic import jsonlogic as jsonLogic

router = APIRouter(prefix="/events", tags=["events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def ingest_event(event: dict, db: Session = Depends(get_db)):
    matched = 0
    wfs = db.query(Workflow).filter(Workflow.is_active == True).all()
    for wf in wfs:
        try:
            if jsonLogic(wf.trigger or {}, event or {}):
                matched += 1
                exec_id = gen_id()
                ex = Execution(id=exec_id, workflow_id=wf.id, context=event)
                db.add(ex); db.commit()
                start = first_node(wf.graph)
                if start:
                    execute_node.delay(exec_id, start)
        except Exception:
            # skip malformed triggers
            continue
    return {"matched": matched}
