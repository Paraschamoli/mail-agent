"""
main.py

FastAPI application - entry point.
All business logic lives in orchestrator.py and agents/*.
Routes are modularized in the routes/ directory.
"""

import os
import base64
import logging
from dotenv import load_dotenv
from fastapi import FastAPI

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider

from mail_agent.database import init_db
from mail_agent.utils import RESUME_DIR, COVER_LETTER_DIR, OTHER_DIR

from mail_agent.routes import (
    applicants_router,
    requirements_router,
    webhook_router,
    misc_router,
)

load_dotenv()

# ── config ────────────────────────────────────────────────────────────────────

for _d in [RESUME_DIR, COVER_LETTER_DIR, OTHER_DIR]:
    os.makedirs(_d, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Langfuse setup (guarded — runs only once) ─────────────────────────────────

def _setup_tracing() -> None:
    """
    Set up Langfuse/OTel tracing exactly once.
    Guard prevents double-init when uvicorn reloads the module
    in its worker process, which caused:
      - WARNING: Overriding of current TracerProvider is not allowed
      - WARNING: Attempting to instrument while already instrumented
    """
    # If a real TracerProvider is already registered, skip entirely
    if isinstance(trace_api.get_tracer_provider(), TracerProvider):
        logger.debug("Tracing already initialized — skipping.")
        return

    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from openinference.instrumentation.agno import AgnoInstrumentor

    PUBLIC = os.getenv("LANGFUSE_PUBLIC_KEY")
    SECRET = os.getenv("LANGFUSE_SECRET_KEY")

    if not PUBLIC or not SECRET:
        raise ValueError("Langfuse keys missing — set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")

    auth = base64.b64encode(f"{PUBLIC}:{SECRET}".encode()).decode()

    exporter = OTLPSpanExporter(
        endpoint="https://cloud.langfuse.com/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {auth}"},
    )

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace_api.set_tracer_provider(provider)

    AgnoInstrumentor().instrument()

    logger.info("Langfuse tracing initialized ✅")


_setup_tracing()

# ── database ──────────────────────────────────────────────────────────────────

init_db()

# ── app ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="HR Triage Agent")

# ── register routes ───────────────────────────────────────────────────────────

app.include_router(webhook_router)
app.include_router(applicants_router)
app.include_router(requirements_router)
app.include_router(misc_router)

# ── entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting on http://0.0.0.0:8000")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    uvicorn.run("mail_agent.main:app", host="0.0.0.0", port=8000)