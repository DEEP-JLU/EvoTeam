# GAIA Dynamic Team Constitution

## Mission

Answer knowledge-intensive GAIA questions with a task-selected team while
keeping one global Chairman: `plan_agent`.

## Team Model

The pool contains public specialist profiles. Before execution, the system
either reuses a task-family template or cold-starts a provisional team. The
Chairman can recruit only the members shown by `list_pool()` for that run.
Templates describe recruitable members, never a Chairman, DAG, assignment,
workflow, capability, skill, or handoff graph.

## Coordination Rules

1. The Chairman selects work and communication dynamically from the visible
   roster; no fixed four-Agent SOP is assumed.
2. Specialists send concrete evidence, calculations, file locations, and
   source URLs back to the Chairman.
3. The Chairman requests verification when evidence conflicts, calculations
   matter, or the final format is strict.
4. The global AnswerAgent is outside templates and is required for every task's
   final answer synthesis. The Chairman sends it the final evidence packet and
   submits exactly its returned answer through the runtime's active submission
   procedure. The exact tool sequence may differ between evaluation and
   evolution runs.
5. Final answers must be concise and match GAIA's requested format exactly.

## Evolution Rules

Agent skills remain private to each Agent. A completed evolved task may create,
retain, or refine only the selected team's template; the global Chairman never
changes with a template.
