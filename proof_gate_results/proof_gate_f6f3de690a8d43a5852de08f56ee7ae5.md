<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_6988f496-b477-49a6-abc8-7232797ea44f?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x2fba633d7b9bfe947cfa7d2d86aef05014b41024",
    "live_context_source": "candidate brief only — no live context file provided",
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
    "Contract holds ~$439k in stablecoins — confirmed by balance tags in triage brief, not independently verified here",
    "At least one public selector exists that moves tokens — UNCONFIRMED, requires bytecode recovery",
    "That selector lacks msg.sender access control — UNCONFIRMED, requires source or decompiled bytecode"
  ],
  "attacker_path": {
    "actor": "",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "stablecoins (~$439k, token addresses unknown)",
    "attacker_gain": "unknown — no selector or withdrawal path identified",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot be assessed without a callable value-moving selector"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Candidate arrived at the proof gate still in NEEDS_LIVE_CONTEXT state. Three hard gates fail: exact_code_path_or_selector_exists is false (verified_source is null, no ABI, no selectors recovered), live_state_supports_preconditions is false (no live context file was provided), and attacker_controls_trigger is false (no callable entrypoint identified). The proof gate cannot advance a candidate that has no confirmed selector or code path. The value signal (~$439k stablecoins, balance spike, unverified contract) is real and non-trivial, but the gate question — does the exact current protocol allow an unprivileged attacker to extract funds — cannot be answered yes or no without bytecode decompilation and selector recovery. Re-route to needs_live_context/ and complete the six live-context steps listed in the triage output (bytecode_and_selector_recovery, proxy_and_implementation_check, token_balance_breakdown, deployer_address_and_funding_trace, transaction_history_and_caller_set, access_control_and_owner_slot) before re-submitting to the proof gate."
}
```

**Why each failing hard gate blocks advancement:**

| Gate | Value | Reason |
|---|---|---|
| `exact_code_path_or_selector_exists` | `false` | `verified_source` is null; no ABI or 4-byte selectors in the brief |
| `live_state_supports_preconditions` | `false` | No live context file was provided; balance tags are scanner signals, not confirmed RPC reads |
| `attacker_controls_trigger` | `false` | No callable entrypoint identified; cannot assert an unprivileged EOA can trigger anything |
| `concrete_fund_or_reward_gain` | `false` | Follows directly from no selector — gain amount and asset are both unknown |
| `gain_is_beyond_entitlement` | `false` | Cannot be evaluated without a confirmed call path |

The proof gate input pipeline defined in `run_generate_proof_gate_pending.py` only pulls from `needs_local_proof/` and `deepwiki_candidates/`. [1](#0-0)  This candidate's triage verdict was `NEEDS_LIVE_CONTEXT`, which routes to `needs_live_context/` per `deepwiki_triage.py`. [2](#0-1)  It should not have entered the proof gate queue; the correct next step is to complete the live-context commands from the triage output and re-triage before re-submitting here.

### Citations

**File:** run_generate_proof_gate_pending.py (L11-11)
```python
    input_dirs = [Path("needs_local_proof"), Path("deepwiki_candidates")]
```

**File:** deepwiki_triage.py (L59-60)
```python
    if verdict == "needs_live_context":
        return Path(os.environ.get("NEEDS_LIVE_CONTEXT_DIR", "needs_live_context"))
```