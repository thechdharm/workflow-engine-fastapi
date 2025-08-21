try:
    from json_logic import jsonLogic
except Exception:
    # fallback import name
    from jsonlogic import jsonlogic as jsonLogic

from ..registry import NodeHandler, HandlerResult, Services

class BranchHandler:
    type = "branch"

    def execute(self, *, node_id: str, data: dict, exec_id: str, payload: dict | None, services: Services) -> HandlerResult:
        cases = data.get("cases", [])
        for case in cases:
            cond = case.get("condition")
            if case.get("else"):
                return HandlerResult(selected_next=case.get("next"))
            try:
                if jsonLogic(cond or {}, payload or {}):
                    return HandlerResult(selected_next=case.get("next"))
            except Exception:
                continue
        return HandlerResult()  # no selection -> end

handler = BranchHandler()
