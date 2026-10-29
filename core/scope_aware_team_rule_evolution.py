from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from core.evolution_models import ScopeAwareTeamRuleEvolutionDecision
from core.team_scoped_rule_guided_collaboration import TeamScopedRuleGuidedCollaborationRegistry


@dataclass
class ScopeAwareTeamRuleEvolutionContext:
    task_id: str
    team_template_id: str
    handoff_family_id: str
    task: str
    actual_agent_ids: list[str]
    current_rules: list[dict[str, Any]] = field(default_factory=list)
    execution_summary: dict[str, Any] = field(default_factory=dict)
    evaluation: dict[str, Any] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    handoff_trace: list[dict[str, Any]] = field(default_factory=list)
    handoff_rule_usage: list[dict[str, Any]] = field(default_factory=list)
    historical_rule_summaries: list[dict[str, Any]] = field(default_factory=list)


class ScopeAwareTeamRuleEvolutionError(ValueError):
    pass


CompletionCallable = Callable[..., Awaitable[Any]]


class LLMScopeAwareTeamRuleEvolutionReflector:
    MAX_REPAIR_ATTEMPTS = 2

    def __init__(self, *, model: str, completion: CompletionCallable | None = None,
                 api_tracker: Any | None = None) -> None:
        self.model = model
        self._completion = completion
        self._api_tracker = api_tracker

    async def reflect(self, context: ScopeAwareTeamRuleEvolutionContext) -> ScopeAwareTeamRuleEvolutionDecision:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the post-task reflector for reusable information handoffs "
                    "between agents. Call record_handoff_decision exactly once. Do not "
                    "create a workflow, DAG, task assignment, agent skill, capability "
                    "list, or team template. A handoff rule is a directed information "
                    "contract for one sender and one receiver within a handoff family.\n\n"
                    "Scope each rule to a directed sender-recipient pair within the "
                    "current team. Preserve distinct rule_id values when the same pair "
                    "requires different contracts under different triggers; do not "
                    "overwrite a different rule merely because its endpoints match.\n\n"
                    "Ground every claim in the actual handoff trace, execution outcome, "
                    "evaluation, failures, or existing rule history. Distinguish a bad "
                    "handoff from an API/provider failure, missing capability, or task "
                    "assignment error; do not encode those unrelated failures as protocol "
                    "guidance. Do not infer a stable preference from a single unsupported "
                    "observation.\n\n"
                    "Record generalizable collaboration patterns, not one-task details. "
                    "Do not mention concrete filenames, class names, module names, PR names, "
                    "repository names, benchmark names, issue numbers, or other "
                    "benchmark-specific objects. Prefer reusable guidance about what the "
                    "receiver needs, evidence/provenance and uncertainty, acceptance or "
                    "verification information, communication style, agreed conventions, "
                    "and a sensible fallback when information is incomplete.\n\n"
                    "Treat the current rule as a living record: preserve guidance that is "
                    "still supported, remove or correct claims contradicted by newer "
                    "evidence, and add only information that improves future handoffs. "
                    "The named fields are a stable minimum schema, not a fixed prose "
                    "template. Use context_notes for important nuances that do not fit "
                    "the other fields; do not force information into a field or discard it "
                    "just because it is unusual.\n\n"
                    "A single failed task is not sufficient evidence to remove a member or "
                    "retire a rule that has successful historical support. Removal/retirement "
                    "is justified only when historical evidence or the current trace clearly "
                    "shows that the member or rule is: (1) persistently mismatched with the "
                    "family collaboration pattern; (2) redundant with another member or rule; "
                    "(3) misleading or harmful in execution; (4) repeatedly misrecruited or "
                    "causing ineffective handoffs; or (5) replaced by a more stable and accurate "
                    "rule. Otherwise preserve it or add a separate rule.\n\n"
                    "A normal task or evaluation failure is valid handoff evidence. When the "
                    "failure is grounded in this interaction, you may create a missing reusable "
                    "positive contract, refine an existing contract, retain a contract while "
                    "recording the evidence, retire only under the historical standard above, "
                    "or choose no_update. Do not create a separate negative-rule type and do not "
                    "turn a one-off failure into a blanket prohibition. Express any improvement "
                    "as positive, actionable guidance about the information, evidence, "
                    "verification, or fallback the receiver needs."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "task_id": context.task_id,
                    "team_template_id": context.team_template_id,
                    "handoff_family_id": context.handoff_family_id,
                    "task": context.task,
                    "actual_agent_ids": context.actual_agent_ids,
                    "current_rules": context.current_rules,
                    "execution_summary": context.execution_summary,
                    "evaluation": context.evaluation,
                    "failures": context.failures,
                    "handoff_trace": context.handoff_trace,
                    "handoff_rule_usage": context.handoff_rule_usage,
                    "historical_rule_summaries": context.historical_rule_summaries,
                    "instruction": (
                        "Use create when this task provides a useful new handoff contract, "
                        "refine when one identified existing contract needs correction, retain when it "
                        "remains useful, retire only with the explicit historical evidence standard "
                        "above, and no_update when evidence is insufficient. For create/refine "
                        "provide a concise semantic handoff_rule_id (lowercase words separated by '_' or '-'; it may include a broad domain such as history or finance), trigger_description, instruction, payload_schema, required_evidence, "
                        "verification, fallback, and optional context_notes. These fields may "
                        "be concise and need not all be populated when not applicable. The "
                        "trigger_description must state the reusable semantic condition for selecting "
                        "this rule; do not encode task-specific routing rules. For refine, "
                        "return a complete merged replacement, keep valid prior guidance, "
                        "remove obsolete one-off observations, and explain what was retained, "
                        "removed, and added in reason. For no_update, use empty from_agent and "
                        "to_agent rather than inventing a pair. A failed evaluation is eligible "
                        "for every action in the action schema when the evidence is tied to this "
                        "handoff; do not invent a negative-rule type."
                    ),
                }, ensure_ascii=False),
            },
        ]
        validation_errors: list[str] = []
        for attempt in range(self.MAX_REPAIR_ATTEMPTS + 1):
            response = await self._call(messages)
            calls = self._extract_calls(response)
            try:
                if len(calls) != 1:
                    raise ValueError(
                        f"expected exactly one record_handoff_decision tool call, got {len(calls)}"
                    )
                decision = ScopeAwareTeamRuleEvolutionDecision(
                    action=str(calls[0].get("action") or "").strip().lower(),
                    handoff_family_id=context.handoff_family_id,
                    rule_id=str(calls[0].get("rule_id") or "").strip(),
                    from_agent=str(calls[0].get("from_agent") or "").strip(),
                    to_agent=str(calls[0].get("to_agent") or "").strip(),
                    reason=str(calls[0].get("reason") or "").strip(),
                    instruction=str(calls[0].get("instruction") or "").strip(),
                    trigger_description=str(calls[0].get("trigger_description") or "").strip(),
                    payload_schema=calls[0].get("payload_schema") or {},
                    required_evidence=[str(x) for x in calls[0].get("required_evidence", [])],
                    verification=str(calls[0].get("verification") or "").strip(),
                    fallback=str(calls[0].get("fallback") or "").strip(),
                    context_notes=str(calls[0].get("context_notes") or "").strip(),
                    evidence={"team_template_id": context.team_template_id},
                )
                decision.validate()

                if decision.action == "no_update":
                    if decision.rule_id or decision.from_agent or decision.to_agent:
                        raise ValueError(
                            "no_update requires empty rule_id, from_agent, and to_agent"
                        )
                    return decision

                actual_agents = set(context.actual_agent_ids)
                if decision.from_agent not in actual_agents or decision.to_agent not in actual_agents:
                    raise ValueError(
                        "handoff agents must participate in this task; "
                        f"actual agents: {sorted(actual_agents)}"
                    )
                observed_pairs = {
                    (str(item.get("from_agent") or ""), str(item.get("to_agent") or ""))
                    for item in context.handoff_trace
                }
                if observed_pairs and (decision.from_agent, decision.to_agent) not in observed_pairs:
                    raise ValueError(
                        "handoff decision must target an observed interaction; "
                        f"observed pairs: {sorted(observed_pairs)}"
                    )

                rules_by_key = {
                    (
                        str(rule.get("handoff_family_id") or ""),
                        str(rule.get("handoff_rule_id") or rule.get("rule_id") or ""),
                    ): rule
                    for rule in context.current_rules
                }
                rule_key = (decision.handoff_family_id, decision.rule_id)
                if decision.action == "create" and rule_key in rules_by_key:
                    raise ValueError(
                        "create rule_id already exists within handoff family: "
                        f"{decision.handoff_family_id}/{decision.rule_id}; "
                        "use refine/retain/retire for that rule"
                    )
                if decision.action in {"refine", "retain", "retire"}:
                    current = rules_by_key.get(rule_key)
                    if current is None:
                        raise ValueError(
                            f"{decision.action} requires an existing rule_id; "
                            "known rule ids in this handoff family: "
                            f"{sorted(key[1] for key in rules_by_key if key[0] == decision.handoff_family_id)}"
                        )
                    expected_pair = (
                        str(current.get("from_agent") or ""),
                        str(current.get("to_agent") or ""),
                    )
                    if (decision.from_agent, decision.to_agent) != expected_pair:
                        raise ValueError(
                            f"rule_id {decision.rule_id} belongs to pair {expected_pair}, "
                            f"not {(decision.from_agent, decision.to_agent)}"
                        )
                return decision
            except (TypeError, ValueError) as exc:
                error = str(exc) or exc.__class__.__name__
                validation_errors.append(error)
                if attempt >= self.MAX_REPAIR_ATTEMPTS:
                    break
                messages.append({
                    "role": "user",
                    "content": (
                        "Your previous handoff decision was invalid. Repair it and return "
                        "exactly one record_handoff_decision tool call. Do not repeat the "
                        f"same error. Validation error: {error}"
                    ),
                })

        return ScopeAwareTeamRuleEvolutionDecision(
            action="no_update",
            handoff_family_id=context.handoff_family_id,
            from_agent="",
            to_agent="",
            rule_id="",
            reason="handoff reflection invalid after two semantic repair attempts",
            evidence={
                "team_template_id": context.team_template_id,
                "reflection_status": "invalid_after_repair",
                "repair_attempts": self.MAX_REPAIR_ATTEMPTS,
                "validation_errors": validation_errors,
            },
        )

    async def _call(self, messages: list[dict[str, str]]) -> Any:
        completion = self._completion
        if completion is None:
            from core.llm import complete
            completion = complete
        return await completion(
            model=self.model,
            messages=messages,
            tools=[self._tool_schema()],
            temperature=0.1,
            max_tokens=1800,
            api_tracker=self._api_tracker,
        )

    @staticmethod
    def _extract_calls(response: Any) -> list[dict[str, Any]]:
        from core.llm import extract_tool_calls
        return [
            dict(call.get("arguments") or {})
            for call in extract_tool_calls(response)
            if call.get("name") == "record_handoff_decision"
            and isinstance(call.get("arguments"), dict)
        ]

    @staticmethod
    def _tool_schema() -> dict[str, Any]:
        return {"type": "function", "function": {
            "name": "record_handoff_decision",
            "description": "Record one team-scoped interaction-rule decision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "refine", "retain", "retire", "no_update"]},
                    "rule_id": {
                        "type": "string",
                        "description": "Stable id of this specific handoff rule. Required for create/refine/retain/retire; empty only for no_update.",
                    },
                    "from_agent": {"type": "string"},
                    "to_agent": {"type": "string"},
                    "reason": {"type": "string"},
                    "instruction": {"type": "string"},
                    "trigger_description": {
                        "type": "string",
                        "description": "Semantic condition for selecting this rule; may include a broad domain such as history or finance.",
                    },
                    "payload_schema": {"type": "object"},
                    "required_evidence": {"type": "array", "items": {"type": "string"}},
                    "verification": {"type": "string"},
                    "fallback": {"type": "string"},
                    "context_notes": {"type": "string"},
                },
                "required": ["action", "reason", "rule_id"],
                "additionalProperties": False,
            },
        }}
