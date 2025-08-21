import requests
from ..registry import NodeHandler, HandlerResult, Services

class HttpCallHandler:
    type = "http_call"

    def execute(self, *, node_id: str, data: dict, exec_id: str, payload: dict | None, services: Services) -> HandlerResult:
        method = data.get("method", "GET").upper()
        url = data.get("url")
        headers = data.get("headers", {}) or {}
        body = data.get("body")
        # naive templating: replace {{payload.xxx}} tokens in url/body
        def tpl(s: str) -> str:
            if not isinstance(s, str): return s
            out = s
            if payload:
                # very simple dot access for one level
                import re
                for m in re.findall(r"{{\s*payload\.([a-zA-Z0-9_\.]+)\s*}}", s):
                    cur = payload
                    for part in m.split("."):
                        cur = cur.get(part, None) if isinstance(cur, dict) else None
                    out = out.replace("{{payload."+m+"}}", str(cur))
            return out
        url = tpl(url)
        if isinstance(body, str):
            body = tpl(body)
        resp = requests.request(method, url, headers=headers, json=body if isinstance(body, dict) else None, data=None if isinstance(body, dict) else body, timeout=20)
        return HandlerResult(result={"status_code": resp.status_code, "text": resp.text[:500]})
        
handler = HttpCallHandler()
