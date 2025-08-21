
def echo_handler(payload, config):
    return {"echo": payload}

def add_handler(payload, config):
    x = config.get("x", 0)
    y = config.get("y", 0)
    return {"sum": x + y, "input": payload}

HANDLERS = {
    "echo": echo_handler,
    "add": add_handler,
}