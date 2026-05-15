---
name: microsoft-docs
description: "Use when the task references any Microsoft, Azure, .NET, VS Code, GitHub Copilot, Windows, PowerShell, M365, Entra, or Power Platform product, API, SDK, CLI, or feature — including how-to, reference lookup, troubleshooting, error messages, deployment, configuration, RBAC, quotas, regions, pricing surfaces, and code samples. Wraps the official Microsoft Learn MCP server and enforces the search-then-fetch workflow."
argument-hint: "[topic or question to look up on Microsoft Learn]"
---

# Microsoft Docs (Microsoft Learn MCP)

Authoritative lookup for anything Microsoft, Azure, .NET, VS Code, Copilot, Windows, PowerShell, M365, Entra, or Power Platform. Training memory on Microsoft topics is stale; this skill is the only sanctioned source.

## Mandatory Workflow

You **MUST** follow this sequence. A `PreToolUse` hook denies `microsoft_docs_fetch` if no `microsoft_docs_search` has run in the current session — there is no path around it.

1. **Search first.** Call `microsoftdocs/mcp/microsoft_docs_search` with a focused natural-language query. Returns up to 10 chunks (≤500 tokens each) with title, URL, and excerpt.
2. **Read the excerpts.** Decide whether the search results already answer the question. If yes, cite the URLs and stop — do not fetch.
3. **Fetch only when depth is required.** If a result needs the full page (tutorial body, prerequisites, full code, reference table not in the excerpt), call `microsoftdocs/mcp/microsoft_docs_fetch` with the URL from the search results.
4. **For code examples**, prefer `microsoftdocs/mcp/microsoft_code_sample_search` (returns up to 20 snippets, optional `language` filter). Still requires a prior `microsoft_docs_search` call — the hook gates *fetch*, but search-first remains the discipline for samples too.
5. **Cite every claim.** Every Microsoft fact in your output must link to the exact Microsoft Learn URL it came from.

## When to Use This Skill

Auto-invoke this skill whenever the task involves:

- Azure services (any), Azure CLI, Azure PowerShell, ARM/Bicep
- .NET, C#, F#, ASP.NET, EF Core
- VS Code, Copilot, GitHub Copilot configuration
- Windows OS, WSL, PowerShell, Windows Terminal
- Microsoft 365, Entra ID, Graph API, Teams, SharePoint
- Power Platform (Power Apps, Power Automate, Power BI)
- Visual Studio, MSBuild, NuGet
- Any error message containing "Microsoft", "Azure", "Az.", "Microsoft.*"
- Any documentation request that says "Microsoft docs", "Azure docs", "Learn", "MS Learn"

## Anti-Patterns (Do Not Do)

- Do **not** answer Microsoft questions from training memory.
- Do **not** call `microsoft_docs_fetch` before `microsoft_docs_search`. The hook will deny it; you will waste a tool call.
- Do **not** fetch every search result reflexively. The excerpts often suffice; fetch only what you need.
- Do **not** paraphrase Microsoft documentation without including the source URL.

## Failure Modes

- **`microsoft_docs_fetch` returned `permissionDecision: deny` with reason "search-first required"** → you skipped step 1. Run `microsoft_docs_search` for the topic, then retry the fetch.
- **Search returned no relevant results** → reformulate with more specific terminology (product + version + error code) before falling back to web search.
- **Search results are stale or contradictory** → fetch the most recent dated page and prefer it.
