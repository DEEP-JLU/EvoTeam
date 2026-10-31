---
name: reflection
description: "Lead the team through post-task reflection to improve future performance. Use this skill when reflection/evolution is enabled after a task is completed."
---

# Reflection Skill — Chairman's Post-Task Improvement Protocol

## When to Use This Skill

Use this skill after completing a task when reflection is enabled. The system will inform you
in the system context if reflection is enabled.

## How Reflection Works

The system manages reflection **automatically**. You do NOT need to send messages to agents
telling them to reflect — the system broadcasts the enabled reflection phase instructions directly.

Your job in each phase is to **complete your own reflection**, not to coordinate others.

## Phase 1: Self-Reflection (L1)

The system automatically sends L1 instructions to all agents. Focus on **your own** performance:

- Did you analyze the issue correctly?
- Was your initial delegation effective? Did you provide enough context in the dispatch?
- Did you recruit the right agents? Was the reviewer needed?
- How could you improve your dispatch quality?

Use `update_prompt_patch` or `update_skill` to record improvements.
Call `skip_l1_reflection` when done.

**Do NOT send messages to other agents during L1.** The system has already given them instructions.

## Optional Phase 2: Cross-Agent Reflection (legacy L2)

L2 runs only when `teammate_profiles_enabled` is explicitly enabled. It is
disabled by default because canonical family-scoped handoff rules supersede it.

1. **Update teammate profiles**: Use `update_teammate_profile` to record your assessment of each agent you worked with.
2. Do not create private correlation files or invent handoff rules. The canonical handoff reflector separately summarizes actual agent-to-agent traces into the family-level `handoff_rules.json` store.
3. Call `skip_l2_reflection` when done.

Only discuss with a teammate if there was a concrete collaboration problem. Skip discussion by default.

Structural team, template, and handoff evolution runs after evaluation through
the adapter-level reflectors. There is no in-session structural reflection phase.

## Important

- Keep reflections concise and actionable
- Focus on patterns that will help in future tasks, not just this one
- The evolution system will persist improvements across task runs
- Don't spend more than 2-3 tool calls per enabled phase — efficiency matters
