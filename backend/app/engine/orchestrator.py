import os
from datetime import datetime
from celery import Celery
from loguru import logger
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Execution, Step, StepStatus, ExecutionStatus
from .graph import next_nodes, find_node
from .registry import registry, Services, HandlerResult
from ..utils import gen_id

# register built-in handlers
from .handlers.send_notification import handler as send_notification_handler
from .handlers.delay import handler as delay_handler
from .handlers.http_call import handler as http_call_handler
from .handlers.branch import handler as branch_handler

registry.register(send_notification_handler)
registry.register(delay_handler)
registry.register(http_call_handler)
registry.register(branch_handler)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("engine", broker=REDIS_URL, backend=REDIS_URL)

def _db() -> Session:
    return SessionLocal()

def _mark_exec_started(db: Session, execution_obj: Execution) -> None:
    if execution_obj.status == ExecutionStatus.PENDING:
        execution_obj.status = ExecutionStatus.RUNNING
        execution_obj.started_at = datetime.utcnow()
        db.commit()

@celery_app.task(name="execute_node")
def execute_node(execution_id: str, node_id: str, resume_from_id: str | None = None) -> None:
    db = _db()
    exec_obj = db.query(Execution).filter(Execution.id == execution_id).first()
    if not exec_obj:
        logger.error(f"Execution {execution_id} not found")
        return

    wf = exec_obj.workflow
    graph = wf.definition

    _mark_exec_started(db, exec_obj)

    # special resume path (used by delay): compute next from resume_from_id
    if node_id == "__RESUME_AFTER__" and resume_from_id:
        next_node_ids = next_nodes(resume_from_id, graph)
        if not next_node_ids:
            _maybe_finish_execution(db, exec_obj)
            return
        for next_id in next_node_ids:
            execute_node.delay(execution_id, next_id)
        return

    node = find_node(node_id, graph)
    if not node:
        logger.warning(f"Node {node_id} not found; finishing if no more work")
        _maybe_finish_execution(db, exec_obj)
        return

    # create step
    step = Step(
        id=gen_id(),
        execution_id=execution_id,
        node_id=node_id,
        type=node.get("type", "unknown"),
        status=StepStatus.RUNNING,
        started_at=datetime.utcnow(),
    )
    db.add(step)
    db.commit()
    db.refresh(step)

    try:
        handler = registry.get(node.get("type"))
        result: HandlerResult = handler.execute(
            node_id=node_id,
            data=node.get("data") or {},
            exec_id=execution_id,
            payload=exec_obj.context or {},
            services=Services(),
        )
        step.status = StepStatus.SUCCEEDED
        step.finished_at = datetime.utcnow()
        step.output = result.result or {}
        db.commit()

        if result.halted:
            # e.g., delay scheduled the resume task
            return

        # if handler selected a next, honor it (branch)
        if result.selected_next:
            execute_node.delay(execution_id, result.selected_next)
            return

        # else follow graph edges
        next_node_ids = next_nodes(node_id, graph)
        if not next_node_ids:
            _maybe_finish_execution(db, exec_obj)
            return
        # fan-out: enqueue all next nodes
        for next_id in next_node_ids:
            execute_node.delay(execution_id, next_id)

    except Exception as error:
        step.status = StepStatus.FAILED
        step.finished_at = datetime.utcnow()
        step.error = {"message": str(error)}
        exec_obj.status = ExecutionStatus.FAILED
        exec_obj.finished_at = datetime.utcnow()
        db.commit()
        logger.exception(error)

def _maybe_finish_execution(db: Session, exec_obj: Execution) -> None:
    # finish if all steps have succeeded or none pending/running
    if exec_obj.status not in (ExecutionStatus.FAILED, ExecutionStatus.CANCELLED):
        exec_obj.status = ExecutionStatus.SUCCEEDED
        exec_obj.finished_at = datetime.utcnow()
        db.commit()