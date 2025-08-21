# from ..registry import NodeHandler, HandlerResult, Services
# from ..graph import next_nodes
# # from ..orchestrator import execute_node  # Celery task

# class DelayHandler:
#     type = "delay"

#     def execute(self, *, node_id: str, data: dict, exec_id: str, payload: dict | None, services: Services) -> HandlerResult:
#         ms = int(data.get("ms", 0))
#         if ms <= 0:
#             return HandlerResult()
#         # schedule next node after delay
#         # orchestrator will determine the next target(s) from the graph by resuming from this node
#         # To simplify, we schedule the immediate next node (first edge) here.
#         # The orchestrator task will compute the graph; but we need the next id.
#         # We'll pass special resume flag by scheduling a separate task that knows to move next.
#         execute_node.apply_async(args=[exec_id, "__RESUME_AFTER__", node_id], countdown=ms/1000.0)
#         return HandlerResult(halted=True)

# handler = DelayHandler()


from ..registry import NodeHandler, HandlerResult, Services
from ..graph import next_nodes

class DelayHandler:
    type = "delay"

    def execute(
        self,
        *,
        node_id: str,
        data: dict,
        exec_id: str,
        payload: dict | None,
        services: Services,
    ) -> HandlerResult:
        ms = int(data.get("ms", 0))
        if ms <= 0:
            return HandlerResult()

        # 🔥 lazy import to avoid circular dependency
        from ..orchestrator import execute_node

        # schedule next node after delay
        execute_node.apply_async(
            args=[exec_id, "__RESUME_AFTER__", node_id],
            countdown=ms / 1000.0,
        )
        return HandlerResult(halted=True)

handler = DelayHandler()
