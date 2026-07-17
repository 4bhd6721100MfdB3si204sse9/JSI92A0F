<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_6d72b83f-4163-48fb-8fde-b63ee5e09666?mode=deep -->

The address `0xaa390a37006e22b5775a34f2147f81ebd6a63641` has no entry in any pipeline state file in this repository. [1](#0-0) [2](#0-1) [3](#0-2) 

All hard gates fail: no source code, no confirmed selectors, no live balances, no attacker path, no gain calculation. Per `HUNT_PLAN.md` the hard stop requires all four conditions proven before promotion. [4](#0-3) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0xaa390a37006e22b5775a34f2147f81ebd6a63641",
    "live_context_source": "none — address absent from state/ethereum_chain_scanner.json, state/latest_targets.json, and state/latest_deepwiki_briefs.json",
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
  "rejection_reason": "Address 0xaa390a37006e22b5775a34f2147f81ebd6a63641 is absent from all pipeline state files (ethereum_chain_scanner.json, latest_targets.json, latest_deepwiki_briefs.json). No source code, ABI, bytecode selectors, live balances, deployer attribution, or token composition exist in the pipeline. The upstream triage verdict is NEEDS_LIVE_CONTEXT, which is a pre-gate state — the candidate has not satisfied the evidence requirements in HUNT_PLAN.md §Evidence Required (live balances, exact entrypoints, entitlement calculation, attacker gain calculation, state diff) and cannot advance to NEEDS_LOCAL_PROOF or HIGH_CONFIDENCE_CANDIDATE. The contradictory verified_source/unknown_verification_status tags further prevent any selector hypothesis. All twelve hard gates fail. Resubmit only after live recon (recon_bravo_then_corecritical) resolves source code, proxy status, token balances, deployer, and at least one value-moving public selector."
}
```

### Citations

**File:** state/ethereum_chain_scanner.json (L1-5)
```json
{
  "last_scanned_block": 100,
  "seen_contracts": {
    "0x1212121212121212121212121212121212121212": {
      "created_at_ms": null,
```

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

**File:** HUNT_PLAN.md (L110-116)
```markdown
Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```