<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_32a0835c-f62c-4196-96aa-a90bbfecea64?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x8e76ebb1c71939982c9ac267c0eb25f4aa739535",
    "live_context_source": "candidate brief only — no separate live context file provided",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": true,
    "live_state_supports_preconditions": false,
    "unprivileged_attacker": false,
    "attacker_controls_trigger": false,
    "exact_code_path_or_selector_exists": false,
    "concrete_fund_or_reward_gain": false,
    "gain_is_beyond_entitlement": false,
    "not_dos_grief_or_liveness_only": true,
    "not_admin_governance_or_key_compromise": true,
    "not_external_dependency_only": true,
    "not_expected_behavior": true,
    "not_known_duplicate": true
  },
  "live_preconditions": [
    "Contract bytecode must be decompiled to recover selectors before any code path can be confirmed",
    "At least one public or external value-moving selector must exist with no msg.sender guard",
    "Contract must still hold the ~$328K balance at the time of the proof attempt",
    "Deployer and funding cluster must be confirmed as non-honeypot before a fork test is meaningful"
  ],
  "attacker_path": {
    "actor": "unknown — cannot be confirmed without selectors",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token(s) held by contract not identified",
    "attacker_gain": "unquantifiable — no selector or withdrawal path confirmed",
    "victim_or_protocol_loss": "unquantifiable",
    "why_gain_exceeds_entitlement": "cannot be established without a confirmed code path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Five hard gates fail simultaneously: live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, and concrete_fund_or_reward_gain are all false. The root blocker is exact_code_path_or_selector_exists: the contract is unverified, no bytecode decompilation was performed, and no ABI or selector was recovered. Without at least one confirmed value-moving selector, no attacker path can be constructed, no preconditions can be validated against live state, and no gain can be quantified. The triage stage correctly returned NEEDS_LIVE_CONTEXT; that live context was never resolved before this gate was invoked. The candidate must complete the five live-context steps listed in the triage output — bytecode decompilation, token balance breakdown, proxy slot check, deployer cluster check, and transaction history review — and be re-submitted to triage before it can be re-evaluated at the proof gate. The $328K balance spike and unverified status are scoring signals, not proof. A high score does not satisfy any hard gate."
}
```

**Gate outcome: REJECT — live context gap, not a safety determination.**

The proof gate is a binary pass/fail on hard gates, not a risk ranking. [1](#0-0)  The decisive failure is `exact_code_path_or_selector_exists = false`: without bytecode decompilation there is no selector, no code path, and therefore nothing the gate can evaluate. [2](#0-1) 

The triage stage's `NEEDS_LIVE_CONTEXT` verdict was correct and was never resolved before this gate was called. [3](#0-2)  The candidate should be routed back to live enrichment (bytecode + selector extraction), then re-submitted to triage, before it reaches the proof gate again.

### Citations

**File:** HUNT_PLAN.md (L17-18)
```markdown

If the answer is not proven against live state or a reproducible fork state, do not promote it.
```

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```

**File:** sentinel_deepwiki_schema.py (L66-79)
```python
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
```