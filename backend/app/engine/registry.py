from typing import Protocol, Any, Optional, Dict
from pydantic import BaseModel

class Services(BaseModel):
    # placeholder for DI: http client, db, logger, etc.
    pass

class HandlerResult(BaseModel):
    result: Optional[dict] = None
    # set selected_next when a node (e.g., branch) wants to override graph traversal
    selected_next: Optional[str] = None
    # when True, orchestrator should stop after this node (e.g., delay scheduled resume)
    halted: bool = False

class NodeHandler(Protocol):
    type: str
    def execute(self, *, node_id: str, data: dict, exec_id: str, payload: dict | None, services: Services) -> HandlerResult: ...

class NodeRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, NodeHandler] = {}

    def register(self, handler: NodeHandler) -> None:
        self._handlers[handler.type] = handler

    def get(self, type_: str) -> NodeHandler:
        if type_ not in self._handlers:
            raise KeyError(f"No handler registered for type {type_}")
        return self._handlers[type_]

    def list(self) -> list[dict[str, Any]]:
        return [{"type": k} for k in self._handlers.keys()]

registry = NodeRegistry()
