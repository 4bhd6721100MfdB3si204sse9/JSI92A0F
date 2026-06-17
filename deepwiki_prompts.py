from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sentinel_deepwiki_schema import proof_gate_contract_json, triage_contract_json


DEFAULT_BLUEPRINT_PATH = Path("blueprints/sentinel_fund_reward_discovery.json")


def load_blueprint(path: str | Path | None = None) -> dict[str, Any]:
    blueprint_path = Path(path or os.environ.get("SENTINEL_BLUEPRINT_PATH", DEFAULT_BLUEPRINT_PATH))
    return json.loads(blueprint_path.read_text(encoding="utf-8"))


def candidate_triage_prompt(candidate_brief: str, blueprint: dict[str, Any] | None = None) -> str:
    blueprint = blueprint or load_blueprint()
    return f"""# DEEPWIKI SENTINEL CANDIDATE TRIAGE

## Mission
Decide whether this Sentinel-discovered live smart-contract candidate is worth local proof work for concrete fund extraction or reward extraction.

DeepWiki cannot run local tests or prove final exploitability in this automation pass. Do not call anything confirmed, validated, proven, or submission-ready.

## Target Scope
{_blueprint_text(blueprint)}

## Candidate Brief
```json
{candidate_brief}
```

## Hard Rules
- Attacker must be unprivileged.
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.

## Output
Return only JSON matching this contract:

```json
{triage_contract_json()}
```
"""


def proof_gate_prompt(candidate: str, live_context: str = "", blueprint: dict[str, Any] | None = None) -> str:
    blueprint = blueprint or load_blueprint()
    context = live_context.strip() or "No separate live context file was provided. Use the candidate brief and list missing live commands."
    return f"""# DEEPWIKI SENTINEL EXACT PROOF GATE

## Gate Question
Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

DeepWiki cannot run local tests. This gate creates proof-ready work only; it does not validate or confirm a report.

## Target Scope
{_blueprint_text(blueprint)}

## Candidate
```json
{candidate}
```

## Live Context
```json
{context}
```

## Output
Return only JSON matching this contract:

```json
{proof_gate_contract_json()}
```
"""


def _blueprint_text(blueprint: dict[str, Any]) -> str:
    lines = [
        f"Project: {blueprint.get('project_name', 'Protocol Sentinel')}",
        f"Paid impact focus: {blueprint.get('paid_impact_focus', '')}",
        f"Gate question: {blueprint.get('gate_question', '')}",
        "",
        "Priority surfaces:",
        *_bullets(blueprint.get("priority_surfaces", [])),
        "",
        "Exploit families:",
        *_bullets(blueprint.get("exploit_families", [])),
        "",
        "Reject:",
        *_bullets(blueprint.get("reject_classes", [])),
    ]
    return "\n".join(lines)


def _bullets(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values]

