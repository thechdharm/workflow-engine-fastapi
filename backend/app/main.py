from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .api.workflows import router as workflows_router
from .api.events import router as events_router
from .api.executions import router as executions_router

app = FastAPI(title="Workflow Orchestration Engine (FastAPI)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(workflows_router)
app.include_router(events_router)
app.include_router(executions_router)
