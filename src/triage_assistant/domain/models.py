"""DCI domain models — the core data shapes shared across all application layers.

All models are Pydantic BaseModels so they validate on construction and serialise
to/from JSON automatically. No infrastructure or AI imports belong here.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# The four valid classification outcomes — enforced at the type level so an
# invalid category can never reach the Application or Infrastructure layers.
TriageCategory = Literal[
    "Data Patch",
    "Engineering Ticket",
    "Field Support",
    "Needs Human Review",
]

# Maps each classification category to the DCI team responsible for it.
# Used by HelpdeskClient when setting assigned_team on the created ticket.
ROUTING_MAP: dict[str, str] = {
    "Data Patch": "Damage Analytics Team",
    "Engineering Ticket": "Engineering Backlog",
    "Field Support": "Field Support Desk",
    "Needs Human Review": "Triage Lead",
}


class HelpRequest(BaseModel):
    """Inbound DCI support request received at POST /api/triage.

    All fields are required — a missing field means the request cannot be
    classified and TriageService will return a Needs Human Review result.
    """

    request_id: Optional[str] = None  # Server-generated ULID; stamped by API handler before entering the pipeline
    submitted_by: str        # Full name of the person submitting the request
    date_submitted: str      # ISO 8601 date string, e.g. "2026-03-10"
    subject: str             # One-line summary of the issue
    description: str         # Full free-text description of the problem
    account_id: str          # DCI account the request is filed against


class TriageMeta(BaseModel):
    """Observability metadata stamped onto every TriageResult by the agent.

    Captures which model produced the classification, how many tokens were
    consumed, and when — useful for cost tracking and audit.
    """

    model: str        # Model identifier as returned by the inference endpoint
    tokens_used: int  # Total tokens (prompt + completion) for the inference call
    timestamp: str    # UTC ISO 8601 timestamp of when classify() completed


class TriageResult(BaseModel):
    """AI classification result returned from POST /api/triage.

    Produced by TriageAgent.classify() and enriched by TriageService before
    being returned to the caller. If confidence falls below the configured
    threshold, TriageService overrides classification to Needs Human Review.
    """

    classification: TriageCategory              # One of the four routing categories
    rationale: str                              # Model's explanation for the classification
    confidence: float = Field(..., ge=0.0, le=1.0)  # Model's self-reported confidence (0–1)
    resolution: Optional[str] = None           # Suggested resolution text, if the model provided one
    follow_up_question: Optional[str] = None   # Question to ask the requester when more info is needed
    meta: Optional[TriageMeta] = None          # Observability metadata; None in unit tests
    ticket_id: Optional[str] = None            # Helpdesk ticket ID set by TriageService after ticket creation
    request_id: Optional[str] = None           # Echoes the server-generated ULID back to the caller (ADR-0006)
