## Reflection Phase — Overview

Task execution is complete. Reflection work records evidence-based improvements for future tasks. Agent patches, skills, teammate profiles, team templates, and team-scoped interaction rules are persisted in their respective memory stores.

**Agent Self-Reflection**: Each agent reflects on its own performance and records reusable improvements to its behavioral patches or skills.

**Teammate Profile Reflection**: Only agents enabled by the profile settings participate. With the default Chairman-only setting, the Chairman records stable, task-relevant capability observations about recruited teammates. Teammate profiles contain general capability observations; directed handoff contracts are handled separately by the team-scoped handoff reflector.

After evaluation, adapter-level reflectors use the execution trace, outcomes, and relevant history to assess reusable team-template membership and team-scoped interaction rules. These decisions are separate from individual agent behavior and teammate profiles.

The system manages the agent-facing reflection transitions automatically. Complete the current stage using its provided tools and wait for the next stage. Adapter-level evolution runs separately after evaluation.
