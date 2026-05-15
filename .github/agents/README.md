# GitHub Copilot Agents

Files in this folder define **custom Copilot agent configurations** — reusable, task-focused personas that give Copilot a specific set of instructions, tools, and behaviors for a particular workflow.

## How It Works

Each file follows the naming pattern `<name>.agent.md`. When you invoke a named agent in Copilot Chat (e.g., `@workspace` or a custom agent), it uses the file's instructions to shape its responses and tool usage.

## Example Agents for This Hackathon

Teams might create agents for common, repeated tasks:

| File | Purpose |
| -- | -- |
| `triage-reviewer.agent.md` | Reviews a triage classification decision and checks it against routing rules |
| `test-writer.agent.md` | Generates pytest test cases for a given application service or module |
| `adr-writer.agent.md` | Drafts an Architecture Decision Record given a problem and options |
| `code-reviewer.agent.md` | Reviews code for Clean Architecture violations and DDD anti-patterns |

## Template

```markdown
---
name: My Agent
description: What this agent does and when to use it.
tools:
  - search/codebase
  - terminal
---

# Agent Instructions

You are a [role]. When asked to [task], you will:

1. Step one
2. Step two
3. Step three

Always follow the conventions in `.github/instructions/`.
```

> **Reference:** [GitHub Copilot coding agent docs](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent)
