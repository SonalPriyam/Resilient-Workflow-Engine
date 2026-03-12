import httpx
import random
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ExternalExecutor:

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def call_external_api(self, url: str, payload: dict):
        async with httpx.AsyncClient() as client:
            if random.random() < 0.3:
                print(f" [Simulated Failure] Network glitch calling: {url}")
                raise httpx.ConnectError("Temporary connection failure")

            print(f" Calling external service: {url}")
            return {"status": "success", "data": "Verified by External Provider"}

    def execute_manual_review(self, request_id: int):
        return {
            "action": "PENDING_HUMAN_APPROVAL",
            "request_id": request_id,
            "note": "Decision diverted to manual queue."
        }