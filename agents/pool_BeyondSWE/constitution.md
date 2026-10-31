# BeyondSWE Engineering Team

## Mission

Fix real-world software bugs in large-scale open source repositories. Deliver correct, minimal patches that pass all tests. Supports cross-repository bug fixes, domain-specific bug fixes, and dependency migrations.

## Environment

- **Working directory**: Provided per-task in the task description — it is **NOT** always `/app`. Read it from the task.
- **Each `docker_bash` runs in a fresh subshell** — `cd` does not persist. Always: `cd {workdir} && ...`
- **Control output length** — always use `head -N` or `tail -N` to avoid truncation waste
- **Prefer `docker_str_replace_editor`** for file edits — more reliable than sed for multi-line changes

## File System Guidelines

- **Path Handling**: Do NOT assume paths are relative to the working directory. Explore the file system first.
- For global search-and-replace, use `sed` instead of opening editors multiple times.
- **Editing vs. Creating**: Modify original files directly. NEVER create multiple versions with suffixes (e.g., file_test.py, file_fix.py).
- **Cleanup**: Delete temporary reproduction scripts once the fix is confirmed.
- When reproducing bugs or implementing fixes, use a single file rather than multiple versions.

## Environment Conservation

- Avoid reinstalling or upgrading packages already in the environment unless strictly necessary.
- If dependencies are missing, first look for dependency files (requirements.txt, pyproject.toml, etc.) and use them.
- Only install individual packages directly if no dependency files exist.

## Hard Constraints

- **NEVER** `git checkout --` — discards all changes
- **NEVER** `git commit` — evaluation extracts patches via `git diff HEAD`
- **NEVER** modify test files — only fix source code
- **NEVER** use interactive tools (vi, nano, less) — they will hang
- **NEVER** use `git fetch`, `git pull`, `git clone`, or access GitHub API — blocked by security policy

## Efficiency

- Each action is expensive. Combine multiple actions when possible (e.g., multiple bash commands in one, use sed/grep to edit/view multiple files at once).
- Use efficient tools like `find`, `grep`, `sed`, and `git` with appropriate filters.
