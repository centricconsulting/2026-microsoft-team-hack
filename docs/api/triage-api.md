# DCI Triage Assistant — API Reference

**Base URL (local):** `http://localhost:8000`  
**Base URL (production):** TBD  
**OpenAPI / Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI JSON:** `http://localhost:8000/openapi.json`

All requests and responses use `application/json`.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/triage` | Classify and route an inbound support request |
| `GET` | `/patterns` | Surface root-cause patterns across ticket history |
| `GET` | `/health` | Liveness check |

---

## POST /triage

Validates, classifies, and routes an inbound support request. Creates a work item in the DCI Helpdesk system. Returns the classification with rationale, confidence score, optional resolution suggestion, and the created ticket ID.

### Request

```json
{
  "request_id": "REQ0001",
  "submitted_by": "Marcus Webb",
  "date_submitted": "2026-03-10",
  "subject": "Export button broken on site status report",
  "description": "When I click the Export to CSV button on the Site Status report page, nothing happens. I've tried Chrome and Edge. This was working fine last week.",
  "account_id": "ACC-1042"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `request_id` | `string` | ✅ | Unique identifier for the inbound request |
| `submitted_by` | `string` | ✅ | Full name of the person submitting the request |
| `date_submitted` | `string` | ✅ | ISO 8601 date (`YYYY-MM-DD`) |
| `subject` | `string` | ✅ | Short one-line summary of the issue |
| `description` | `string` | ✅ | Full description of the problem |
| `account_id` | `string` | ✅ | DCI account identifier for the requester |

Missing required fields cause an automatic `Needs Human Review` classification with `follow_up_question` specifying the missing data.

### Response

```json
{
  "classification": "Engineering Ticket",
  "rationale": "The request describes a UI button that stopped functioning after previously working. This is consistent with a software regression and requires a developer to investigate and fix the application code.",
  "confidence": 0.94,
  "resolution": "Create an engineering work item and assign to the AppDev team.",
  "follow_up_question": null,
  "ticket_id": "TKT-20483",
  "meta": {
    "model": "gpt-4o",
    "tokens_used": 312,
    "timestamp": "2026-03-10T09:14:22Z"
  }
}
```

| Field | Type | Nullable | Description |
|---|---|---|---|
| `classification` | `string` | ❌ | One of the four routing categories (see below) |
| `rationale` | `string` | ❌ | LLM-generated explanation for the classification |
| `confidence` | `float` | ❌ | Confidence score `[0.0, 1.0]`; below `0.85` escalates to `Needs Human Review` |
| `resolution` | `string` | ✅ | Suggested resolution grounded in historical cases |
| `follow_up_question` | `string` | ✅ | Populated when `classification` is `Needs Human Review` |
| `ticket_id` | `string` | ✅ | ID of the work item created in the DCI Helpdesk |
| `meta.model` | `string` | ✅ | Azure OpenAI deployment used |
| `meta.tokens_used` | `integer` | ✅ | Total tokens consumed by the classification call |
| `meta.timestamp` | `string` | ✅ | ISO 8601 UTC timestamp of the classification |

### Classification Categories

| Category | Routed To | Trigger |
|---|---|---|
| `Data Patch` | Damage Analytics Team | Data-only fix; SQL INSERT/UPDATE/DELETE; no code change needed |
| `Engineering Ticket` | Engineering Backlog | Bug, regression, or feature request requiring a developer |
| `Field Support` | Field Support Desk | Portal access, certifications, how-to, contractor onboarding |
| `Needs Human Review` | Triage Lead | Ambiguous, insufficient information, or confidence < 0.85 |

### Error Responses

| Status | Condition |
|---|---|
| `422 Unprocessable Entity` | Request body fails Pydantic schema validation |
| `500 Internal Server Error` | Azure OpenAI call failed or Helpdesk API unreachable |

---

## GET /patterns

Returns an LLM-narrated summary of root-cause patterns detected across historical ticket data.

### Response

```json
{
  "patterns": [
    "25% of Engineering Tickets in Q1 2026 relate to the Site Status report page — indicating a systemic instability in that module.",
    "Field Support requests spike on Monday mornings, suggesting contractor onboarding bottlenecks at week start.",
    "Data Patch tickets are concentrated in accounts with IDs in the ACC-10xx range — likely a cohort migrated from the legacy system."
  ],
  "analysed_record_count": 50,
  "meta": {
    "model": "gpt-4o",
    "tokens_used": 820,
    "timestamp": "2026-03-10T09:20:00Z"
  }
}
```

---

## GET /health

Liveness check. Returns `200 OK` when the application is running and the SK kernel is initialised.

```json
{ "status": "ok" }
```

---

## Running Locally

```bash
uv run uvicorn triage_assistant.api.main:app --reload
```

Then open `http://localhost:8000/docs` for interactive Swagger UI.  
All 10 sample requests are also pre-loaded in [triage.http](../../triage.http) for the VS Code REST Client extension.

---

## References

- [ADR-0001: Python Triage Architecture](../adr/ADR-0001-python-triage-architecture.md)
- [ADR-0002: API Framework](../adr/ADR-0002-api-framework.md)
- [data/help_requests/sample_requests.json](../../data/help_requests/sample_requests.json)
- [DCI Helpdesk OpenAPI Spec](https://app-x2slazjwhcxuq.azurewebsites.net/openapi/v1.json)
