# Workspace-Wide Copilot Instructions

## File Safety — No Irreversible Destructive Actions via Terminal

**Never use terminal commands to create, modify, or permanently destroy files in this workspace.**

This includes (but is not limited to):
- `dotnet new` — do not scaffold projects or files via the CLI
- `echo`, `cat`, `tee`, `cp`, `mv` redirected to files
- Any command that writes to disk as a side effect
- `rm`, `rm -rf`, `git clean` — permanent deletion is forbidden

**Always use the editor tools instead:**
- `edit/createFile` to create new files
- `edit/editFiles` to modify existing files

### Deleting a File — Use the Workspace Recycle Bin

To delete a file, **move it to `.trash/` at the workspace root** rather than using `rm`. This keeps the action reversible.

```
mv <path/to/file> /workspaces/2026-microsoft-team-hack/.trash/<filename>
```

- Create `.trash/` with `mkdir -p .trash` if it does not exist (this one `mkdir` is permitted).
- The file can be recovered by moving it back. The folder is gitignored.
- Only use this after explicit user approval for the specific file.

Terminal use is permitted **only** for read-only or build/run operations:
- `dotnet build` — verify compilation
- `dotnet test` — run tests
- `dotnet run` — start the application
- `dotnet user-secrets` — manage secrets (does not modify source files)
- `git status`, `git log` — read-only git inspection
- `grep`, `find`, `ls`, `cat` — read-only inspection

**Rationale:** Terminal commands that write files bypass the editor's change tracking, have overwritten in-progress work in this repository before, and are harder to review and reverse. Irreversible destruction (e.g. `rm`) is never permitted — move to `.trash/` instead.
