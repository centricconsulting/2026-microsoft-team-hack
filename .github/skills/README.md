# GitHub Copilot Skills

Agent skills are **directories of instructions and scripts** that Copilot loads when relevant to a task. Each skill lives in its own subdirectory here and must contain a `SKILL.md` file.

> **Skills vs. instructions:** Use `.github/instructions/*.instructions.md` for general coding standards Copilot should always know. Use skills for detailed, task-specific workflows Copilot should only apply when relevant.

## Structure

```
.github/skills/
├── scaffold-usecase/
│   └── SKILL.md
├── generate-triage-prompt/
│   └── SKILL.md
└── add-otel-logging/
    ├── SKILL.md
    └── add-otel-logging.sh   # optional scripts/resources
```

## Creating a Skill

1. Create a subdirectory with a lowercase, hyphenated name:
   ```
   .github/skills/my-skill-name/
   ```

2. Add a `SKILL.md` file (must be named exactly `SKILL.md`):

   ```markdown
   ---
   name: my-skill-name
   description: What this skill does. Be specific — Copilot uses this to decide when to invoke it.
   ---

   Step-by-step instructions for Copilot to follow when this skill is invoked.
   Reference any scripts in this directory by filename.
   ```

3. Optionally add scripts or resource files alongside `SKILL.md`.

## Using a Skill

Copilot automatically invokes skills when your prompt matches the `description`. You can also invoke one directly:

```
Use the /scaffold-usecase skill to create a TriageRequest use case.
```

## CLI Commands

| Command | Purpose |
| -- | -- |
| `/skills list` | List all available skills |
| `/skills info <name>` | Show details and location for a skill |
| `/skills reload` | Reload skills after adding one mid-session |
| `/skills` | Toggle skills on/off interactively |

## Example Skills for This Hackathon

| Directory | Description |
| -- | -- |
| `scaffold-usecase/` | Scaffold a Clean Architecture use case with request, response, and handler |
| `generate-triage-prompt/` | Build a structured system prompt for the AI triage endpoint |
| `add-otel-logging/` | Add OpenTelemetry structured logging to an existing class or endpoint |
| `write-adr/` | Draft an Architecture Decision Record from a problem statement and options |

## Finding Community Skills

Browse ready-made skills at [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/). Download a skill directory and place it here, then run `/skills reload`.

> **Reference:** [GitHub Copilot — Add skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

