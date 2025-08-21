from ..registry import NodeHandler, HandlerResult, Services

class SendNotificationHandler:
    type = "send_notification"

    def execute(self, *, node_id: str, data: dict, exec_id: str, payload: dict | None, services: Services) -> HandlerResult:
        # For demo: print; in real life: integrate Slack/Email/SMS
        to_role = data.get("toRole", "AE")
        message = data.get("message", "New event")
        print(f"[notify] exec={exec_id} role={to_role} message={message}")
        return HandlerResult(result={"notified": to_role, "message": message})

handler = SendNotificationHandler()
