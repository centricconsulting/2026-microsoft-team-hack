---
applyTo: "**/*.csproj,**/Program.cs,**/*.sln"
---

# .NET Project Conventions

## Target Framework

Use **.NET 9** or later for all projects.

```xml
<TargetFramework>net9.0</TargetFramework>
```

## Solution Structure

Follow Clean Architecture with four projects:

```
src/
  DCI.Triage.Domain/           # Entities, value objects, domain interfaces — no dependencies
  DCI.Triage.Application/      # Use cases, handlers, DTOs — depends on Domain only
  DCI.Triage.Infrastructure/   # AI clients, HTTP, persistence — depends on Application
  DCI.Triage.Api/              # Minimal API or Azure Functions host — depends on all layers
tests/
  DCI.Triage.Domain.Tests/
  DCI.Triage.Application.Tests/
  DCI.Triage.Infrastructure.Tests/
```

## NuGet Packages

| Purpose | Package |
| -- | -- |
| AI (Azure OpenAI) | `Azure.AI.OpenAI` |
| AI orchestration | `Microsoft.SemanticKernel` |
| Minimal API | Built into `Microsoft.AspNetCore.App` |
| Dependency injection | Built into `Microsoft.Extensions.DependencyInjection` |
| Testing | `xunit`, `xunit.runner.visualstudio` |
| Mocking | `FakeItEasy` |
| Assertions | `FluentAssertions` |
| OpenTelemetry | `OpenTelemetry.Extensions.Hosting`, `OpenTelemetry.Instrumentation.AspNetCore` |
| HTTP client | `Microsoft.Extensions.Http` |

## Configuration

- Store secrets in `dotnet user-secrets` locally; use Azure Key Vault or environment variables in deployed environments
- Never commit API keys or connection strings
- Use `IOptions<T>` pattern for strongly typed configuration

## Minimal API Convention

Register endpoints in extension methods, not inline in `Program.cs`:

```csharp
// Program.cs
app.MapTriageEndpoints();

// TriageEndpoints.cs
public static class TriageEndpoints
{
    public static IEndpointRouteBuilder MapTriageEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("/api/triage", async (...) => { ... });
        return app;
    }
}
```

## Observability

- Use `ILogger<T>` for structured logging throughout
- Include correlation IDs in all log entries touching the AI layer
- Export traces via OpenTelemetry to Azure Monitor or the Aspire Dashboard
