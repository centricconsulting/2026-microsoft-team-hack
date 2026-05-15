#!/usr/bin/env bash
# PreToolUse hook: reminds agents to read and update ADRs when editing source files.
# Written in bash — no Python stdlib dependency.

input=$(cat)

# Extract tool name using grep (handles the JSON field "tool":"...")
tool=$(echo "$input" | grep -o '"tool":"[^"]*"' | head -1 | sed 's/"tool":"//;s/"//')

# Only intercept file creation/edit tools
if [[ "$tool" != "edit/createFile" && "$tool" != "edit/editFiles" ]]; then
    exit 0
fi

# Extract file path
path=$(echo "$input" | grep -o '"path":"[^"]*"' | head -1 | sed 's/"path":"//;s/"//')
# Also check filePaths array for editFiles
if [[ -z "$path" ]]; then
    path=$(echo "$input" | grep -o '"filePaths":\["[^"]*"' | head -1 | sed 's/"filePaths":\["//;s/"//')
fi

# Only intercept edits to src/ or tests/
if [[ "$path" != *"src/"* && "$path" != *"tests/"* ]]; then
    exit 0
fi

# Check if ADRs have been read this session — we can't track this perfectly in bash,
# so we emit an "ask" to remind the agent every time it touches source files.
cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "ADR Compliance check: Before modifying source files, confirm you have read docs/adr/ADR-0001 through ADR-0004. Ensure your changes match the API contract, model field names, and config keys defined there. If your change diverges from an ADR, update the ADR in the same step. Proceed if ADRs have been reviewed."
  }
}
EOF
