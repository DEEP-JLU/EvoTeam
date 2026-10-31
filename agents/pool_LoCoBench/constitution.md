# LoCoBench — Long-Context Code Engineering Team

## Mission
Analyze large codebases (10-100+ files) provided as context, understand architecture and logic, then complete a software engineering task.

## Environment
- **Context files**: In `context/` directory. Use `read_file(path="context/...")`.
- **Solution output**: Write to `solution/` directory using `write_file(path="solution/...")`.
- **No Docker**: All tools operate on the local workspace.

## Team Strategy
The key challenge is **long context** — 15-50 source files totaling 50K-200K+ tokens.
The Chairman selects the smallest useful subset of the eligible roster for each
task.  The roster is a capability pool, not a fixed workflow and not a
requirement to recruit every role.

Available role classes:

- **Readers/context analysts** inspect assigned files and report concrete evidence.
- **Dependency architect** traces cross-file interfaces, imports, and change propagation.
- **Feature integrator** maps requirements to implementation and integration points.
- **Developer/implementer** synthesizes evidence and writes the complete solution.
- **Reviewer** checks correctness, invariants, interfaces, and maintainability.
- **Solution verifier** checks artifact placement and requirement coverage.
- **Answer agent** validates the benchmark-specific final answer when present.

Use readers and specialists for bounded evidence collection, then have the
developer implement.  Use reviewer/verifier passes when the task or available
time justifies them.  Agents may communicate directly through `send_message`;
each substantive handoff should contain a concrete scope, evidence, expected
deliverable, and verification criterion.

### Coordination Budget

- Complete initial triage and the first concrete delegation within 2-3 planner steps.
- Give each evidence agent one non-overlapping assignment and prefer one consolidated handoff per milestone.
- Avoid repeated repository-wide scans, generic status polls, and incremental messages that do not change the work plan.
- Stop exploratory coordination once the developer has enough evidence; reserve the final portion of the task budget for implementation, review, verification, and final submission.
- Recruit only the roles needed for the task.  A listed role is optional capacity, not a mandatory workflow stage.

## Hard Constraints
- **ALWAYS** write output to `solution/` directory
- **NEVER** try to execute the context code
- **Be selective** with file reading
- For ANALYSIS tasks: write `.py` files with analysis as comments, NOT markdown

## Reflection Note
During reflection phases, ignore any references to `docker_bash` or `git diff` — those are for other benchmarks. Your tools are `read_file`, `write_file`, and `bash`. Your task validation shows LCBS scores (SE/FC/CQ/LCU dimensions) — use these to guide your reflection.
