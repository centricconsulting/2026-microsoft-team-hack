---
applyTo: "**/*.cs"
---

# C# Coding Standards

## Naming Conventions

| Element | Convention | Example |
| -- | -- | -- |
| Classes, records, interfaces | PascalCase | `TriageRequest`, `ITriageService` |
| Methods, properties | PascalCase | `ClassifyAsync`, `Confidence` |
| Private fields | `_camelCase` | `_openAiClient` |
| Parameters, local variables | camelCase | `helpRequest`, `result` |
| Constants | PascalCase | `MaxRetries` |
| Interfaces | `I` prefix | `ITriageHandler` |

## Records vs Classes

- Prefer **records** for DTOs, requests, and responses (immutable by default)
- Use **classes** for services, handlers, and domain objects with behavior

```csharp
// ✅ Record for request/response
public record TriageRequest(string RequestId, string Subject, string Description);
public record TriageResponse(string Classification, string Rationale, double Confidence);

// ✅ Class for handlers and services
public class TriageHandler(ITriageService triageService) : ITriageHandler { ... }
```

## Clean Architecture Rules

- **Domain** layer has **zero dependencies** on other layers or NuGet packages (except BCL)
- **Application** layer depends only on Domain; never reference Infrastructure or API types
- **Infrastructure** implements interfaces defined in Application — not the reverse
- **API** layer wires up DI and delegates to Application; contains no business logic

```csharp
// ✅ Correct — Application defines the interface
// Application/Interfaces/IAiTriageService.cs
public interface IAiTriageService
{
    Task<TriageResult> ClassifyAsync(HelpRequest request, CancellationToken ct);
}

// ✅ Correct — Infrastructure implements it
// Infrastructure/AI/AzureOpenAiTriageService.cs
public class AzureOpenAiTriageService(AzureOpenAIClient client) : IAiTriageService { ... }
```

## Async

- All I/O-bound methods must be `async Task<T>` and accept `CancellationToken`
- Suffix async methods with `Async`
- Never use `.Result` or `.Wait()` — always `await`

## Null Handling

- Enable nullable reference types in all projects: `<Nullable>enable</Nullable>`
- Use `ArgumentNullException.ThrowIfNull()` for guard clauses
- Prefer null-coalescing and null-conditional operators over explicit null checks

## Error Handling

- Use a `Result<T>` pattern or typed exceptions in the Domain layer — do not throw raw exceptions from use cases
- Catch and translate infrastructure exceptions at the Infrastructure boundary
- Return `400 Bad Request` for validation errors, `500` for unhandled faults, with a structured error body

## Domain-Driven Design

- **Entities** have identity; **Value Objects** are defined by their values
- Keep domain logic inside the Domain layer — not in handlers or controllers
- Use **use cases** (handlers) in the Application layer to orchestrate domain and infrastructure

```csharp
// Domain value object
public record ConfidenceScore
{
    public double Value { get; }
    public ConfidenceScore(double value)
    {
        if (value is < 0 or > 1)
            throw new ArgumentOutOfRangeException(nameof(value), "Confidence must be between 0 and 1.");
        Value = value;
    }
}
```

## Testing

- Test class names: `{SystemUnderTest}Tests`
- Test method names: `{Method}_{Scenario}_{ExpectedResult}`
- Use **FakeItEasy** for fakes/mocks; use **FluentAssertions** for assertions
- One logical assertion per test; use `[Theory]` + `[InlineData]` for parameterized cases

```csharp
public class TriageHandlerTests
{
    [Fact]
    public async Task HandleAsync_WhenRequestIsVague_ReturnsNeedsHumanReview()
    {
        // Arrange
        var aiService = A.Fake<IAiTriageService>();
        A.CallTo(() => aiService.ClassifyAsync(A<HelpRequest>._, A<CancellationToken>._))
            .Returns(new TriageResult("Needs Human Review", "Insufficient detail", 0.45));

        var handler = new TriageHandler(aiService);

        // Act
        var result = await handler.HandleAsync(new TriageRequest("REQ0006", "Something is broken", ""), default);

        // Assert
        result.Classification.Should().Be("Needs Human Review");
    }
}
```
