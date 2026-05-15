#!/usr/bin/env bash
# PostToolUse hook: runs pytest after every edit to src/ or tests/ to catch regressions immediately.
# The AI cannot override this hook — test failures block progression.

input=$(cat)

# Extract tool name
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

# Only run for edits to src/ or tests/
if [[ "$path" != *"src/"* && "$path" != *"tests/"* ]]; then
    exit 0
fi

# Check if uv and pyproject.toml exist before running
if [[ ! -f "pyproject.toml" ]]; then
    exit 0
fi

if ! command -v uv &> /dev/null; then
    exit 0
fi

# Run pytest and capture output
pytest_output=$(uv run pytest --tb=short -q 2>&1)
pytest_exit=$?

# Exit code 5 = no tests collected — not a failure, skip blocking
if [[ $pytest_exit -eq 5 ]]; then
    exit 0
fi

if [[ $pytest_exit -ne 0 ]]; then
    # Properly escape the reason string as a JSON value using Python stdlib.
    # Raw interpolation into a heredoc breaks JSON when output contains
    # quotes, backslashes, or real newlines.
    reason=$(printf "pytest failed after editing %s. Fix failing tests before continuing.\n\n%s" \
        "$path" "$pytest_output" \
        | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "permissionDecision": "block",
    "permissionDecisionReason": ${reason}
  }
}
EOF
fi
