import json
from sqlalchemy.orm import Session
from app.models import WorkflowRequest, AuditLog, WorkflowStatus
from app.rules import RuleEvaluator
from app.executor import ExternalExecutor

class WorkflowEngine:

    def __init__(self, db: Session, config_path: str):
        self.db = db
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.executor = ExternalExecutor()

    async def execute(self, request_id: int):
        req = self.db.query(WorkflowRequest).filter(WorkflowRequest.id == request_id).first()
        if not req:
            return

        current_step_id = self.config["initial_step"]
        req.status = WorkflowStatus.IN_PROGRESS
        self.db.commit()

        while current_step_id:
            step_cfg = self.config["steps"].get(current_step_id)
            if not step_cfg:
                break

            print(f"Executing step: {current_step_id}")
            
            outcome = "PASSED"
            next_step = None

            if step_cfg["type"] == "RULE_EVALUATION":
                passed = RuleEvaluator.evaluate(req.input_data, step_cfg["condition"])
                outcome = "PASSED" if passed else "FAILED"
                next_step = step_cfg["on_success"] if passed else step_cfg["on_failure"]

            elif step_cfg["type"] == "EXTERNAL_SERVICE":
                try:
                    await self.executor.call_external_api(step_cfg["endpoint"], req.input_data)
                    outcome = "API_SUCCESS"
                    next_step = step_cfg["on_success"]
                except Exception as e:
                    outcome = "API_FAILURE"
                    next_step = step_cfg["on_failure"]

            elif step_cfg["type"].startswith("TERMINAL"):
                req.status = step_cfg["status"]
                next_step = None

            audit = AuditLog(
                request_id=req.id,
                step_name=current_step_id,
                action_type=step_cfg["type"],
                input_snapshot=req.input_data,
                decision_outcome=outcome,
                reasoning=f"Moved to {next_step}" if next_step else "Finished",
                status="SUCCESS"
            )
            self.db.add(audit)
            self.db.commit()

            current_step_id = next_step

        self.db.commit()
        return req