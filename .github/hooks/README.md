# GitHub Copilot Hooks

Hooks let you extend GitHub Copilot agent behavior by running custom shell commands at **key points during agent execution** — before a tool runs, after a prompt is submitted, when a session starts, and more.

## How It Works

Create a JSON file in this folder (e.g., `hooks.json`). Copilot loads it automatically:
- **Copilot CLI:** loaded from the current working directory
- **Copilot cloud agent:** must be present on the repository's default branch

## Hook Triggers

| Trigger | Fires When |
| -- | -- |
| `sessionStart` | An agent session begins |
| `sessionEnd` | An agent session ends |
| `userPromptSubmitted` | A prompt is submitted to the agent |
| `preToolUse` | Before the agent calls any tool |
| `postToolUse` | After a tool call completes |
| `errorOccurred` | An error occurs during agent execution |

## File Format

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "type": "command",
        "bash": "echo \"Session started: $(date)\" >> logs/session.log",
        "powershell": "Add-Content -Path logs/session.log -Value \"Session started: $(Get-Date)\"",
        "cwd": ".",
        "timeoutSec": 10
      }
    ],
    "userPromptSubmitted": [
      {
        "type": "command",
        "bash": "./scripts/log-prompt.sh",
        "powershell": "./scripts/log-prompt.ps1",
        "cwd": "scripts",
        "env": {
          "LOG_LEVEL": "INFO"
        }
      }
    ],
    "preToolUse": [...],
    "postToolUse": [...],
    "sessionEnd": [...],
    "errorOccurred": [...]
  }
}
```

> Remove any triggers you don't need from the `hooks` object.

## Example Ideas for This Hackathon

| Hook | Use Case |
| -- | -- |
| `sessionStart` | Log session start time and working directory |
| `userPromptSubmitted` | Log prompts to a file for the retrospective ("what did teams ask Copilot?") |
| `preToolUse` | Print the tool name and args before execution for debugging |
| `postToolUse` | Validate that generated code compiles (`dotnet build`) after file edits |
| `errorOccurred` | Alert or log when the agent hits an error |

## Troubleshooting

| Issue | Fix |
| -- | -- |
| Hooks not executing | Verify the JSON file is in `.github/hooks/`; check `version: 1` is set; validate JSON with `jq . hooks.json` |
| Scripts not running | Ensure scripts are executable: `chmod +x script.sh`; add a shebang (`#!/bin/bash`) |
| Hooks timing out | Default timeout is 30 seconds; increase `timeoutSec` in the config |

## Debugging a Hook Script

```bash
#!/bin/bash
set -x  # Enable debug mode
INPUT=$(cat)
echo "DEBUG: Received input" >&2
echo "$INPUT" >&2
```

Test locally by piping input into your script:

```bash
echo '{"timestamp":1704614400000,"cwd":".","toolName":"bash"}' | ./scripts/my-hook.sh
```

> **Reference:** [GitHub Copilot — Use hooks](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks)

