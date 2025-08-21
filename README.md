# Workflow Engine

A workflow orchestration backend built with FastAPI, SQLAlchemy, Celery, Redis, and PostgreSQL. Define workflows as graphs of nodes and execute them with delays, branching, and full execution history.

## What it does

- Define workflows as JSON graphs with different node types
- Trigger workflows based on JSONLogic conditions
- Execute workflows step-by-step with Celery workers
- Built-in nodes: notifications, HTTP calls, delays, conditional branching
- Track execution history and step details
- REST API for workflow management

## Getting started

### Docker (recommended)

```bash
# Start all services
docker compose up --build -d

# Seed the database with sample workflows
docker compose exec api python -m app.scripts.seed
```

The API will be available at http://localhost:8000/docs

### Test it out

Trigger a sample event that matches the seeded workflow:

```bash
curl -X POST http://localhost:8000/events \
  -H 'Content-Type: application/json' \
  -d '{"lead": {"source": "LinkedIn", "score": 90, "title": "CEO"}}'
```

### Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start the API
uvicorn app.main:app --reload

# In another terminal, start Redis and Celery
redis-server
celery -A app.engine.orchestrator.celery_app worker -l info

# Seed the database
python -m app.scripts.seed
```

## API endpoints

### Workflows
- `POST /workflows` - Create a new workflow
- `GET /workflows` - List all workflows
- `GET /workflows/{id}` - Get workflow details
- `PUT /workflows/{id}` - Update workflow
- `DELETE /workflows/{id}` - Delete workflow

### Events
- `POST /events` - Send an event (triggers matching workflows)

### Executions
- `GET /executions?workflow_id=...` - List workflow executions
- `GET /executions/{id}` - Get execution details
- `GET /executions/{id}/steps` - Get execution step details

## Workflow structure

Workflows are defined as JSON graphs with nodes and edges. Each node has a type and data, and edges connect them to form the execution flow.

Example workflow:
```json
{
  "nodes": [
    {"id": "start", "type": "start", "data": {}},
    {"id": "notify", "type": "send_notification", "data": {"toRole": "AE", "message": "New hot lead"}},
    {"id": "wait", "type": "delay", "data": {"ms": 1000}},
    {"id": "call", "type": "http_call", "data": {"method": "POST", "url": "https://httpbin.org/post"}},
    {"id": "branch", "type": "branch", "data": {"cases": [{"label":"CEO","condition":{"==":[{"var":"lead.title"}, "CEO"]},"next":"gift"},{"else": true, "next":"drip"}]}}
  ],
  "edges": [
    {"id":"e1","source":"start","target":"notify"},
    {"id":"e2","source":"notify","target":"wait"},
    {"id":"e3","source":"wait","target":"call"},
    {"id":"e4","source":"call","target":"branch"}
  ]
}
```

## Node types

- **start** - Entry point for workflows
- **send_notification** - Send notifications to roles/users
- **http_call** - Make HTTP requests with templated payloads
- **delay** - Wait for a specified time before continuing
- **branch** - Conditional branching based on JSONLogic expressions

## Adding custom node types

Create a handler in `app/engine/handlers/your_node.py`:

```python
from ..registry import NodeHandler, HandlerResult, Services

class MyNode:
    type = "my_node"
    
    def execute(self, *, node_id, data, exec_id, payload, services):
        # Your custom logic here
        return HandlerResult(result={"ok": True})

handler = MyNode()
```

Register it in `app/engine/orchestrator.py`:

```python
from .handlers.your_node import handler as my_handler
registry.register(my_handler)
```

## How it works

1. **Workflow definition** - Save workflow as JSON graph with nodes and edges
2. **Event ingestion** - POST events to `/events` endpoint
3. **Trigger evaluation** - JSONLogic evaluates if event matches workflow conditions
4. **Execution** - Celery workers execute nodes one by one, following the graph edges
5. **History** - Track execution status, step results, and timing

## Architecture

- **FastAPI** - REST API and event handling
- **SQLAlchemy** - Database models and queries
- **Celery** - Asynchronous task execution
- **Redis** - Message broker and result backend
- **PostgreSQL** - Persistent storage for workflows and executions

## Frontend

The backend is designed to work with any frontend that can:
- Create/edit workflow graphs (React Flow, D3.js, etc.)
- Save workflow definitions to the `/workflows` endpoint
- Trigger executions via `/events`

## Development notes

- Delays use Celery countdown and resume with a special `__RESUME_AFTER__` task
- Branch nodes can override the default graph flow by setting `selected_next`
- HTTP calls support basic templating with `{{payload.field}}` syntax
- All database operations are wrapped in transactions
