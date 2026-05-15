"""DCI Triage Assistant — FastAPI application entry point.

This module is the **composition root** for the entire application. It is the only
place where concrete infrastructure classes (TriageAgent, RagService, HelpdeskClient)
are instantiated and wired together. All other layers (Application, Domain) depend
only on abstract interfaces — never on anything defined here.

Why a composition root?
    Centralising object construction here means the Application layer stays
    framework-agnostic and fully testable without FastAPI or any AI SDK running.
    Swapping an infrastructure adapter (e.g., replacing RagService with an
    Azure AI Search-backed implementation) requires changing exactly one line here.

Startup sequence (lifespan):
    1. Load configuration from .env / environment variables.
    2. Embed all historical cases into the in-memory vector store (RagService.load).
    3. Instantiate the FoundryChatClient-backed TriageAgent.
    4. Wire everything into TriageService and attach it to app.state.

Routes:
    POST /triage   — classify a DCI support request; creates a helpdesk ticket.
    GET  /health   — liveness probe.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from ulid import ULID

# Infrastructure layer — only imported here (the composition root).
# Application and Domain layers never import from infrastructure.
from triage_assistant.config import TriageSettings
from triage_assistant.infrastructure.helpdesk_client import HelpdeskClient
from triage_assistant.infrastructure.rag_service import RagService
from triage_assistant.infrastructure.agents.triage_agent import TriageAgent
from triage_assistant.domain.models import HelpRequest, TriageResult
from triage_assistant.application.triage_service import TriageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler — runs startup logic before serving requests.

    Builds the full object graph exactly once:
      - TriageSettings reads FOUNDRY_PROJECT_ENDPOINT, HELPDESK_API_KEY, and all
        optional tuning parameters from the environment / .env file.
      - RagService.load() embeds every historical case via Azure AI Foundry embeddings
        so cosine-similarity search is available with zero per-request latency.
      - TriageAgent, HelpdeskClient, and TriageService are instantiated with settings
        injected; no global state or singletons are created outside this function.

    Pylance reports the TriageSettings() call as missing required arguments because
    pydantic-settings fills them from environment variables at runtime — the
    type: ignore suppresses that false positive.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        settings = TriageSettings()  # type: ignore[call-arg]

        # Embed all historical cases once at boot — avoids per-request embedding calls.
        rag = RagService(settings)
        await rag.load_historical_cases()

        # TriageAgent owns its FoundryChatClient; one client for the application lifetime.
        agent = TriageAgent(settings)

        helpdesk = HelpdeskClient(settings)

        # Inject interfaces into the Application layer — no AI types cross this boundary.
        app.state.triage_service = TriageService(
            agent, rag, helpdesk,
            confidence_threshold=settings.confidence_threshold,
        )
        logger.info("Triage service ready.")
    except Exception as exc:  # noqa: BLE001
        # Azure credentials unavailable (e.g. local dev without az login).
        # GET / (intake form) and GET /health work without app.state.
        # POST /triage will return 503 until credentials are configured.
        logger.warning("Triage service unavailable: %s. GET / and /health still serve.", exc)
        app.state.triage_service = None

    yield
    # Shutdown: in-memory store requires no teardown.


app = FastAPI(
    title="DCI Triage Assistant",
    description="AI-powered support ticket classification for Damage Control, Inc.",
    version="0.1.0",
    lifespan=lifespan,
)

_templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)


@app.get("/", response_class=HTMLResponse)
async def intake_form(request: Request) -> HTMLResponse:
    """Serve the DCI ticket intake form.

    Returns the Jinja2-rendered intake.html template. The form collects all
    six HelpRequest fields and submits them via JavaScript fetch() to POST /triage,
    so the API contract (ADR-0001) remains unchanged — no python-multipart needed.
    """
    return _templates.TemplateResponse(request, "intake.html")


@app.post("/triage", response_model=TriageResult)
async def triage(request: HelpRequest) -> TriageResult:
    """Classify and route an inbound DCI support request.

    Delegates to TriageService which runs the full pipeline:
      1. Semantic search over historical cases (RAG context).
      2. Azure AI Foundry gpt-4o classification with rationale and confidence score.
      3. Confidence gate — overrides to 'Needs Human Review' if below threshold.
      4. Creates a work item in the DCI helpdesk system.

    Returns a TriageResult containing the classification, rationale, confidence,
    suggested resolution, optional follow-up question, model metadata, and ticket_id.
    """
    if app.state.triage_service is None:
        return JSONResponse(
            status_code=503,
            content={"detail": "Triage service unavailable — Azure credentials not configured. Run 'az login' and restart."},
        )
    request.request_id = str(ULID())
    result = await app.state.triage_service.triage(request)
    return result.model_copy(update={"request_id": request.request_id})


@app.get("/health")
async def health() -> dict:
    """Liveness probe — returns 200 OK when the application is running.

    Does not check downstream dependencies (Foundry, helpdesk). Use this to
    confirm the process is alive; a separate readiness check would verify that
    RagService has finished loading before declaring the instance ready.
    """
    return {"status": "ok"}
