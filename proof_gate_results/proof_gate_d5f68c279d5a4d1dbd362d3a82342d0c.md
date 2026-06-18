<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_1930a356-2918-436e-b865-98fdab25fddc?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "bsc",
    "address": "0x1a9b68ca1dcacb106c4b853e2d9c915f0cfe2e56",
    "live_context_source": "deepwiki_briefs/12-bsc-0x1a9b68ca1dcacb106c4b853e2d9c915f0cfe2e56.json",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": false,
    "live_state_supports_preconditions": false,
    "unprivileged_attacker": false,
    "attacker_controls_trigger": false,
    "exact_code_path_or_selector_exists": false,
    "concrete_fund_or_reward_gain": false,
    "gain_is_beyond_entitlement": false,
    "not_dos_grief_or_liveness_only": false,
    "not_admin_governance_or_key_compromise": false,
    "not_external_dependency_only": false,
    "not_expected_behavior": false,
    "not_known_duplicate": true
  },
  "live_preconditions": [],
  "attacker_path": {
    "actor": "",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "",
    "attacker_gain": "",
    "victim_or_protocol_loss": "",
    "why_gain_exceeds_entitlement": ""
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Candidate arrived at the proof gate with triage verdict NEEDS_LIVE_CONTEXT — the six mandatory live-context items were never resolved. verified_source is null, no 4-byte selectors have been recovered, deployer_address is empty, proxy slot state is unknown, and no calldata-bearing transactions have been observed. Every hard gate that requires an anchored code path (exact_code_path_or_selector_exists, live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, concrete_fund_or_reward_gain, gain_is_beyond_entitlement) is false. The proof gate cannot promote a candidate whose entire attacker path is BLOCKED pending selector recovery. Return this candidate to the live-enrichment stage: execute bytecode_and_selector_recovery, proxy_slot_check, deployer_address_and_funding_trace, recent_transaction_calldata_patterns, token_balance_breakdown, and privileged_caller_set as specified in the triage output, then resubmit with a populated live_context block."
}
```

**Why every blocking gate fails:**

| Hard Gate | Status | Reason |
|---|---|---|
| `exact_code_path_or_selector_exists` | **false** | `verified_source: null`; no bytecode selector recovery has been run |
| `live_state_supports_preconditions` | **false** | No live context file was provided; balance figure is from the brief, not a current RPC snapshot |
| `unprivileged_attacker` | **false** | Cannot confirm any function is publicly callable without access control — no ABI exists |
| `attacker_controls_trigger` | **false** | Call sequence is explicitly `BLOCKED` in the triage output |
| `concrete_fund_or_reward_gain` | **false** | No selector → no confirmed transfer path → no quantifiable gain |
| `gain_is_beyond_entitlement` | **false** | Entitlement calculation requires knowing the accounting model, which requires source code |

The triage stage correctly flagged `NEEDS_LIVE_CONTEXT`. The proof gate does not have that verdict — a candidate that has not cleared live context must `REJECT` here and re-enter the pipeline after the six enrichment commands in the triage output are executed. [1](#0-0) [2](#0-1)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
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