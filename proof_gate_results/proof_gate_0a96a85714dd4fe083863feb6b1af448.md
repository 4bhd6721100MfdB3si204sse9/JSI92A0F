<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_cb419b1e-1b22-4706-8f41-e79f5b8c73ff?mode=deep -->

The address `0xbee3211ab312a8d065c4fef0247448e17a8da000` is absent from every pipeline artifact in this repository. The proof-gate schema (`sentinel_deepwiki_schema.py` lines 52–103) only accepts three verdicts — `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE` — and every hard gate fails because no live state, selectors, or source exist for this address. The correct output is:

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0xbee3211ab312a8d065c4fef0247448e17a8da000",
    "live_context_source": "",
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
    "not_known_duplicate": false
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
  "rejection_reason": "Hard gate failure: current_live_target_only=false. Address 0xbee3211ab312a8d065c4fef0247448e17a8da000 does not appear in state/latest_targets.json, state/latest_deepwiki_briefs.json, or any run artifact in this repository. No live state, verified source, selectors, deployer identity, proxy state, or token balance data is present in the pipeline. All twelve hard gates fail. The upstream triage verdict was NEEDS_LIVE_CONTEXT, which is a triage-schema verdict (sentinel_deepwiki_schema.py TRIAGE_CONTRACT) and is not a valid proof-gate promotion state. This candidate must complete the live-enrichment stage (stages 3–5 of the pipeline) and re-enter the proof gate with a populated live snapshot before any gate can be evaluated."
}
```

**Why every hard gate is false:**

- `current_live_target_only`: The address is not in `state/latest_targets.json` (which contains only the six placeholder addresses) and not in `state/latest_deepwiki_briefs.json`. [1](#0-0) 
- `live_state_supports_preconditions` through `gain_is_beyond_entitlement`: No source, no selectors, no deployer, no proxy state, and no token identity data exist anywhere in the repository for this address. The candidate brief itself lists six blocking `live_context_required` items and marks `call_sequence` and `expected_assertions` as `BLOCKED`. [2](#0-1) 

**Schema note:** `NEEDS_LIVE_CONTEXT` is a verdict defined in `TRIAGE_CONTRACT`, not in `PROOF_GATE_CONTRACT`. The proof gate only accepts `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. A triage result of `NEEDS_LIVE_CONTEXT` must be resolved upstream (pipeline stages 3–5) before the proof gate is invoked. [3](#0-2)

### Citations

**File:** state/latest_targets.json (L1-5)
```json
{
  "targets": [
    {
      "address": "0x7777777777777777777777777777777777777777",
      "category": "migrator vault",
```

**File:** state/latest_deepwiki_briefs.json (L1-5)
```json
[
  "deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json",
  "deepwiki_briefs/002-bsc-0x5555555555555555555555555555555555555555.json",
  "deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json"
]
```

**File:** sentinel_deepwiki_schema.py (L52-55)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "gate_question": (
```