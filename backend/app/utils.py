import uuid

def gen_id() -> str:
    return uuid.uuid4().hex
