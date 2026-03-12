from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.models import Base, WorkflowRequest, AuditLog, WorkflowStatus
from app.engine import WorkflowEngine

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resilient Workflow Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trigger/{workflow_type}")
async def trigger_workflow(
    workflow_type: str,
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    ikey = data.get("idempotency_key")
    if not ikey:
        raise HTTPException(status_code=400, detail="idempotency_key is required")

    existing = db.query(WorkflowRequest).filter(WorkflowRequest.idempotency_key == ikey).first()
    if existing:
        return {"message": "Request already exists", "request_id": existing.id, "status": existing.status}

    new_request = WorkflowRequest(
        idempotency_key=ikey,
        workflow_type=workflow_type,
        input_data=data,
        status=WorkflowStatus.PENDING
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    config_path = f"config/{workflow_type}.json"
    wf_engine = WorkflowEngine(db, config_path)

    background_tasks.add_task(wf_engine.execute, new_request.id)

    return {
        "message": "Workflow started",
        "request_id": new_request.id,
        "status": WorkflowStatus.PENDING
    }

@app.get("/status/{request_id}")
def get_status(request_id: int, db: Session = Depends(get_db)):

    req = db.query(WorkflowRequest).filter(WorkflowRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    logs = db.query(AuditLog).filter(AuditLog.request_id == request_id).all()

    return {
        "request_id": req.id,
        "current_status": req.status,
        "history": [
            {
                "step": log.step_name,
                "outcome": log.decision_outcome,
                "reason": log.reasoning,
                "time": log.timestamp
            } for log in logs
        ]
    }