---
description: >
  Use when working on any DCI feature, support ticket, architecture decision, or domain logic.
  Covers the Damage Control, Inc. business context, bounded contexts, and stakeholder map.
  Load for triage classification, requirements work, architecture design, or any task
  involving DCI domain language, work orders, contractors, incidents, or site management.
---

# DCI Domain Context

## The Business: Damage Control, Inc.

DCI is a **disaster response and reconstruction contractor**. When incidents occur in the
Marvel Universe — structural collapse, alien incursion, fire damage, flooding — DCI is
contracted by **cities, government agencies, and insurers** to manage the full reconstruction
lifecycle:

1. **Incident assessment** — scoping the damage and engaging clients (city liaisons, agencies)
2. **Work order dispatch** — creating and assigning work orders to field crews and specialist subcontractors
3. **Site execution** — debris removal, structural repair, reconstruction across multiple active sites simultaneously
4. **Closure and billing** — finalising work orders, generating invoices, reporting to city council

DCI operates at urban scale across NYC boroughs and beyond. Their internal platform — the
**DCI Operations Portal** — is the operational backbone managing this entire lifecycle.

## Bounded Contexts

When scoping work or reviewing a support ticket, always identify which bounded context owns
the problem:

| Context | What It Owns |
|---|---|
| **Incident Management** | Triggering event, type (structural/fire/alien/flood), location, severity, initial client engagement |
| **Work Order Management** | Work order lifecycle: creation, assignment, scope changes, status, closure |
| **Contractor Management** | Subcontractor onboarding, OSHA certifications, crew rosters, portal access, compliance flags |
| **Site Management** | Physical sites, borough mapping, project-to-site linkage, site status (active/closed) |
| **Project Financials** | Invoicing, billing contacts, change orders, project cost tracking, borough-level cost reporting |
| **Analytics & Reporting** | ETL pipelines, Power BI dashboards, nightly syncs, city liaison and executive reporting |
| **External Integrations** | NYC City Damage Assessment API, third-party field management systems, nightly data syncs |
| **Support Triage** | AI-assisted classification and routing of inbound help desk requests — the system being built |

Cross-context contamination is a smell. If a feature touches more than two contexts, decompose it.

## Bounded Contexts → Solution Mapping

Each bounded context maps to a seam in the Clean Architecture solution. Design these seams now, even before splitting into separate projects:

| Bounded Context | Current Home | Interface Seam |
|---|---|---|
| **Support Triage** | `Application/UseCases/Triage*` | `ITriageClassifier` |
| **Work Order Management** | `Infrastructure/Helpdesk/` | `IHelpdeskClient` |
| **Analytics / Historical Data** | `Infrastructure/History/` | `IHistoricalCaseRepository` |
| **Contractor / Site** | Not in scope for PoC | — |

When a feature grows past its seam, the interface is the stable boundary — not the folder.

## Stakeholder Map

| Role | What They Need |
|---|---|
| **Operations Coordinator** | Real-time visibility into work order status, site progress, contractor compliance |
| **Field Contractor** | Portal access, work order details, change order submission, certification management |
| **Site Supervisor** | View and update work orders for assigned sites; no access to billing |
| **City Liaison / Government Agency** | Incident cost reports, progress dashboards, regulatory compliance evidence |
| **Project Manager** | Project lifecycle oversight, site closure sign-off, resourcing across active projects |
| **Accounting Team** | Invoice generation and delivery, billing contact management, project cost reconciliation |
| **DCI Technology Team** | System reliability, engineering backlog prioritisation, AI triage adoption |
| **Triage Lead** | Manual review queue for tickets the AI cannot confidently classify |
