# GitHub Copilot Instructions

Files in this folder provide **persistent context** to GitHub Copilot about the codebase's conventions, architecture, and standards. Copilot reads these automatically when you're working on matching files.

## How It Works

Each file follows the naming pattern `<topic>.instructions.md` and can be scoped to specific file types using a front-matter `applyTo` glob. When you're editing a file that matches, Copilot uses the instructions as background context — no need to re-explain conventions in every prompt.

## Files in This Folder

| File | Applies To | Purpose |
| -- | -- | -- |
| `python.instructions.md` | `**/*.py` | Python layer rules, Protocol pattern, async/await, pytest, MAF agent pattern |
| `dotnet.instructions.md` | `**/*.cs`, `**/*.csproj` | .NET 9 project setup, SDK choices, and tooling conventions (dormant — no .cs files) |
| `csharp.instructions.md` | `**/*.cs` | C# coding standards, naming conventions, Clean Architecture patterns (dormant — no .cs files) |

## Adding Your Own

Teams are encouraged to add instruction files for their specific choices. Examples:

```
python.instructions.md       # If using Python
typescript.instructions.md   # If using TypeScript / Node.js
testing.instructions.md      # Test patterns and conventions
api.instructions.md          # API design rules for your stack
```

### Template

```markdown
---
applyTo: "**/*.cs"
---

# Topic Instructions

Brief description of what this file governs.

## Convention 1

Explanation.

## Convention 2

Explanation.
```

> **Reference:** [GitHub Copilot customization docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
