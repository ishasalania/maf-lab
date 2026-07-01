"""Production FastAPI application for MAF Incident Response Workflow."""

import asyncio
import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workflow import build_workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("maf-app")

workflow = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global workflow
    if os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL"):
        logger.info("Building MAF incident response workflow...")
        workflow = build_workflow()
        logger.info("Workflow ready.")
    else:
        logger.warning("FOUNDRY_PROJECT_ENDPOINT or FOUNDRY_MODEL not set — workflow disabled. Set env vars and restart.")
        workflow = None
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="MAF Incident Response API",
    description="Production multi-agent workflow for automated incident triage, diagnosis, and remediation.",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# MODELS
# =============================================================================


class IncidentRequest(BaseModel):
    id: str | None = None
    title: str
    service: str
    severity: str = "unknown"
    incident_type: str = "unknown"
    description: str
    environment: str = "production"


class IncidentResponse(BaseModel):
    run_id: str
    incident_id: str
    status: str
    outputs: list[str]
    started_at: str
    completed_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    workflow_ready: bool


# =============================================================================
# ENDPOINTS
# =============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        workflow_ready=workflow is not None,
    )


@app.post("/incidents", response_model=IncidentResponse)
async def process_incident(incident: IncidentRequest):
    """Submit an incident for automated triage and response."""
    if workflow is None:
        raise HTTPException(status_code=503, detail="Workflow not initialized")

    run_id = str(uuid.uuid4())
    incident_id = incident.id or f"INC-{uuid.uuid4().hex[:8]}"
    started_at = datetime.now(timezone.utc).isoformat()

    alert_payload = incident.model_dump()
    alert_payload["id"] = incident_id

    logger.info(f"[{run_id}] Processing incident: {incident.title}")

    try:
        events = await workflow.run(json.dumps(alert_payload))
        outputs = [str(out) for out in events.get_outputs()]
    except Exception as e:
        logger.error(f"[{run_id}] Workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

    completed_at = datetime.now(timezone.utc).isoformat()

    logger.info(f"[{run_id}] Completed with {len(outputs)} outputs")

    return IncidentResponse(
        run_id=run_id,
        incident_id=incident_id,
        status="completed",
        outputs=outputs,
        started_at=started_at,
        completed_at=completed_at,
    )


@app.post("/incidents/stream")
async def stream_incident(incident: IncidentRequest):
    """Submit an incident and stream outputs as Server-Sent Events."""
    if workflow is None:
        raise HTTPException(status_code=503, detail="Workflow not initialized")

    alert_payload = incident.model_dump()
    alert_payload["id"] = incident.id or f"INC-{uuid.uuid4().hex[:8]}"

    async def event_stream():
        try:
            events = await workflow.run(json.dumps(alert_payload))
            outputs = events.get_outputs()
            for i, out in enumerate(outputs):
                data = json.dumps({"index": i, "output": str(out)})
                yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'status': 'completed', 'total_outputs': len(outputs)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
