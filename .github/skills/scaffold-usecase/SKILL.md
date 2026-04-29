---
name: scaffold-usecase
description: >
  Scaffolds a Clean Architecture use case (command/query + handler + response)
  for the DCI Triage Assistant. Use this when adding a new operation to the
  application layer — for example, a TriageRequest use case, a GetTicketHistory
  query, or any new command/query handler pair.
---

# scaffold-usecase

You are scaffolding a Clean Architecture use case for the DCI Triage Assistant. Follow these steps exactly.

## Step 1 — Confirm the use case name and type

Ask the user (or infer from context) for:
- **Name** — PascalCase noun-verb phrase, e.g. `TriageRequest`, `GetTicketHistory`
- **Type** — `Command` (write/side-effect) or `Query` (read-only)
- **Layer path** — the `Application` project folder where files should be created (e.g. `src/DCI.Triage.Application/UseCases/`)

## Step 2 — Create the request record

Create `{Name}{Command|Query}.cs`:

```csharp
namespace DCI.Triage.Application.UseCases;

/// <summary>
/// Input for the <see cref="{Name}Handler"/> use case.
/// </summary>
public sealed record {Name}{Command|Query}(
    // Add strongly-typed parameters here
    string RequestId,
    string Description
);
```

Rules:
- Use `record` (immutable value object)
- Parameters must be strongly typed — no `object` or `Dictionary`
- Name matches the use case exactly

## Step 3 — Create the response record

Create `{Name}Result.cs`:

```csharp
namespace DCI.Triage.Application.UseCases;

/// <summary>
/// Output returned by <see cref="{Name}Handler"/>.
/// </summary>
public sealed record {Name}Result(
    // Add result fields here
    bool IsSuccess,
    string? ErrorMessage = null
);
```

Rules:
- Use `record`
- Include an `IsSuccess` flag and nullable `ErrorMessage` for all command results
- Query results may omit the error fields if they throw on failure instead

## Step 4 — Create the handler

Create `{Name}Handler.cs`:

```csharp
using Microsoft.Extensions.Logging;

namespace DCI.Triage.Application.UseCases;

/// <summary>
/// Handles <see cref="{Name}{Command|Query}"/> requests.
/// </summary>
public sealed class {Name}Handler(
    // Inject domain services and infrastructure interfaces here
    ILogger<{Name}Handler> logger)
{
    public async Task<{Name}Result> HandleAsync(
        {Name}{Command|Query} request,
        CancellationToken cancellationToken = default)
    {
        logger.LogInformation(
            "Handling {UseCaseName} for RequestId={RequestId}",
            nameof({Name}Handler),
            request.RequestId);

        // TODO: implement use case logic

        return new {Name}Result(IsSuccess: true);
    }
}
```

Rules:
- Primary constructor injection only (C# 12+)
- Always inject `ILogger<{Name}Handler>`
- Log at `Information` on entry with structured parameters (no string interpolation)
- Log at `Warning` for expected failures; `Error` only for unexpected exceptions
- Return `{Name}Result` — never throw for expected outcomes
- All public methods are `async Task<T>` unless synchronous is truly justified
- No infrastructure concerns (no EF DbContext, no HttpClient) — inject interfaces

## Step 5 — Register in DI

Add to the application layer's `ServiceCollectionExtensions` (or equivalent):

```csharp
services.AddScoped<{Name}Handler>();
```

## Step 6 — Wire up the API endpoint (optional)

If the user asks for an API endpoint, add a Minimal API route in the API/Infrastructure project:

```csharp
app.MapPost("/api/{route}", async (
    {Name}{Command|Query} request,
    {Name}Handler handler,
    CancellationToken ct) =>
{
    var result = await handler.HandleAsync(request, ct);
    return result.IsSuccess ? Results.Ok(result) : Results.BadRequest(result.ErrorMessage);
})
.WithName("{Name}")
.WithTags("Triage");
```

## Conventions to always follow

- Reference `.github/instructions/csharp.instructions.md` and `.github/instructions/dotnet.instructions.md` for naming and project conventions.
- All files go in the `Application` layer — never in `API` or `Infrastructure`.
- Do not add `using` statements for namespaces within the same assembly unless required.
- Do not create base classes or abstract handlers — each handler is self-contained.
