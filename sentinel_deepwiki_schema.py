from __future__ import annotations

import json
from typing import Any


TRIAGE_CONTRACT: dict[str, Any] = {
    "schema_version": "sentinel-triage-v1",
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "candidate": {
        "source_file": "",
        "chain": "",
        "address": "",
        "name": "",
        "entity_type": "",
        "next_action": "",
        "score": 0,
    },
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "why_this_target_matters": "",
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
    "suspected_exploit_families": [],
    "source_or_selector_basis": [
        {
            "selector_or_function": "",
            "evidence": "",
            "why_it_matters": "",
        }
    ],
    "attacker_path_hypothesis": {
        "actor": "unprivileged external user",
        "preconditions": [],
        "call_sequence": [],
        "expected_gain": "",
    },
    "local_proof_required": {
        "test_type": "fork | unit | invariant | fuzz | manual",
        "setup": [],
        "transaction_sequence": [],
        "expected_assertions": [],
    },
    "rejection_reason": "",
}


PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "gate_question": (
        "Does this exact current protocol, with current live state, allow an "
        "unprivileged attacker to extract funds or rewards beyond entitlement?"
    ),
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "active_target": {
        "chain": "",
        "address": "",
        "live_context_source": "",
        "live_context_is_current": False,
    },
    "hard_gates": {
        "current_live_target_only": False,
        "live_state_supports_preconditions": False,
        "unprivileged_attacker": False,
        "attacker_controls_trigger": False,
        "exact_code_path_or_selector_exists": False,
        "concrete_fund_or_reward_gain": False,
        "gain_is_beyond_entitlement": False,
        "not_dos_grief_or_liveness_only": False,
        "not_admin_governance_or_key_compromise": False,
        "not_external_dependency_only": False,
        "not_expected_behavior": False,
        "not_known_duplicate": False,
    },
    "live_preconditions": [],
    "attacker_path": {
        "actor": "",
        "attacker_inputs": [],
        "call_sequence": [],
        "state_before": [],
        "state_after": [],
    },
    "extraction_analysis": {
        "asset_or_reward": "",
        "attacker_gain": "",
        "victim_or_protocol_loss": "",
        "why_gain_exceeds_entitlement": "",
    },
    "local_proof_required": {
        "test_type": "fork | unit | invariant | fuzz | manual",
        "test_file_to_add": "",
        "setup": [],
        "transaction_sequence": [],
        "expected_assertions": [],
        "reject_if_assertion_fails": "",
    },
    "rejection_reason": "",
}


def triage_contract_json() -> str:
    return json.dumps(TRIAGE_CONTRACT, indent=2)


def proof_gate_contract_json() -> str:
    return json.dumps(PROOF_GATE_CONTRACT, indent=2)

