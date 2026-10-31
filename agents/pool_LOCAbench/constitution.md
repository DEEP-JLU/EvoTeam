# LOCA-bench capability pool

The complete task is the source of truth. Select or create a family from the
actual collaboration pattern, not from the benchmark name, application,
business domain, tool name, or surface vocabulary. A family describes the
work pattern, complementary responsibilities, evidence exchange, validation,
and a short boundary; it does not prescribe a fixed team size.

The chairman remains the coordinator and may choose the smallest useful subset
of the selected family. `answer_agent` is a global final-output service and is
never a family member. Responsibility boundaries are based on work products:
`context_reader` acquires source evidence; `data_analyst` derives selections
and calculations; `cross_system_integrator` designs mappings and operation
order only when multiple systems require them; `artifact_specialist` writes
required local files; `state_operator` performs external-service mutations and
communications; and `verification_agent` independently checks results without
silently repairing them. A single task need not use every stage.

Every external write must be handed off with the intended change, relevant
evidence, and expected postcondition. Avoid concurrent writes to the same
resource and do not repeat a write merely because another agent has not yet
reported. Readers, analysts, integrators, and verifiers remain read-only with
respect to external state. Local scratch calculations are allowed, but only
`artifact_specialist` owns task-required local deliverables.

When a task is compact, do not expand the team just because additional roles
exist in the pool. Add a role only when the complete task requires its distinct
capability. Preserve successful family members and handoff rules unless direct
evidence shows redundancy, mismatch, harm, repeated ineffective recruitment,
or replacement by a more reliable rule.

## Bulk execution protocol

For multi-record tasks, determine the complete target count before writing and
store the exact target-to-payload mapping in
`workspace/agent_workspace/task_manifest.json`. Store stable parameters in
`task_params.json`. Split large manifests into non-overlapping executor ranges:
one executor for up to 80 items, two for 81-160, and all suitable executors
above 160. Large lists must be passed through files rather than long messages.
Each executor reports its exact range, completed count, failed count, and
method, and updates the manifest at checkpoints. The coordinator must reconcile
all ranges and independently read back the final state. If an executor is
silent for two minutes, stop waiting, inspect its range, and take over the
remaining work. A partial range or narrative completion is never sufficient.

## Conditional PRIMARY/FALLBACK handoff

Mutation handoffs must name the normal MCP path and a task-specific fallback
path. Use MCP first. Switch to local_db only after a fatal, non-recoverable MCP
error; stop calling the failed tool after that point. Do not switch for a normal
parameter-validation error or a task-level mistake. The fallback report must
include the exact range, `completed/failed/remaining` counts, and whether the
MCP or local_db path was used. Fallback writes require independent read-back
verification before the coordinator can finalize the task.
