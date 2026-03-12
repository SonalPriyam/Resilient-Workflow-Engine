# Resilient Workflow & Rules Engine Platform

A robust, state-machine-based workflow engine built with **FastAPI** and **SQLAlchemy**. This platform is designed to handle complex business processes (like Loan Approvals or Employee Onboarding) with a focus on engineering robustness, auditability, and configurability.

##  Key Features

* **Dynamic Rules Engine:** Define business logic in JSON using JSONPath—no code changes required to update thresholds.
* **Engineering Robustness:** Built-in **Idempotency** checks to prevent duplicate processing and **Exponential Backoff Retries** for external API failures.
* **Full Auditability:** Every decision, input snapshot, and transition is logged in a relational database for 100% transparency.
* **Generic Architecture:** The same engine handles multiple workflow types (Loan Approval, Onboarding, etc.) via configuration.

##  Tech Stack

* **Framework:** FastAPI (Asynchronous API)
* **Database:** SQLite with SQLAlchemy ORM
* **Resilience:** Tenacity (Retry logic) & HTTPX (Async client)
* **Logic:** JSONPath-NG for dynamic rule evaluation
* **Testing:** Pytest with FastAPI TestClient


Install all dependencies that is in requirements.txt


Running the Application:

Start the server using Uvicorn:
 Go to Bash and write :- python -m uvicorn api.routes:app --reload


Example Usage (Loan Approval)
Endpoint: POST /trigger/loan_approval

Payload:
        {
            "idempotency_key": "unique_id_123",
            "name": "Jane Doe",
             "age": 28,
            "credit_score": 720
        }


Explainability: Use GET /status/{request_id} to see the full audit trail of why the loan was approved or rejected.