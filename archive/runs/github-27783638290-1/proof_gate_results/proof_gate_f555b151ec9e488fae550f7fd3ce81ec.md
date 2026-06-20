<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_3b321fa5-9fc4-48be-9f30-18f614817713?mode=deep -->

The address `0xf8e349d1d827a6edf17ee673664cfad4ca78c533` does not appear anywhere in the repository — no file, no state entry, no brief. [1](#0-0)  The `deepwiki_briefs/` directory contains only three placeholder briefs, none for this address. [2](#0-1)  The hard gates defined in `HUNT_PLAN.md` require a reproducible path, confirmed live state, and known selectors before promotion. [3](#0-2) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0xf8e349d1d827a6edf17ee673664cfad4ca78c533",
    "live_context_source": "none — address absent from state/ethereum_chain_scanner.json and deepwiki_briefs/",
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
    "not_dos_grief_or_liveness_only": true,
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
  "rejection_reason": "Address 0xf8e349d1d827a6edf17ee673664cfad4ca78c533 is absent from all repository live state files (state/ethereum_chain_scanner.json contains only placeholder addresses; deepwiki_briefs/ holds no entry for this address; glob search returns zero matches). Four hard gates fail: current_live_target_only=false (not in live state), live_state_supports_preconditions=false (no enrichment data), exact_code_path_or_selector_exists=false (verified_source null, no ABI, no decompiled selectors), concrete_fund_or_reward_gain=false (TVL figure originates from the candidate brief alone, not from a repository-tracked live snapshot). Per HUNT_PLAN.md hard stop: a candidate must show an unprivileged attacker, a reproducible path, extraction of user funds or excess rewards, and gain beyond entitlement — none of these can be established without first completing live enrichment. Required before re-submission: (1) bytecode decompilation to recover selectors, (2) token balanceOf query to confirm current TVL, (3) deployer trace to rule out honeypot or rug-redeploy, (4) EIP-1967 proxy slot check, (5) transaction history review for privileged-only call patterns."
}
```

### Citations

**File:** state/ethereum_chain_scanner.json (L1-10)
```json
{
  "last_scanned_block": 100,
  "seen_contracts": {
    "0x1212121212121212121212121212121212121212": {
      "created_at_ms": null,
      "deployer": "",
      "deployment_tx": "0xtransfer01",
      "discovery_source": "erc20_transfer_log",
      "first_seen_block": 100,
      "last_seen_block": 100,
```

**File:** state/latest_deepwiki_briefs.json (L1-5)
```json
[
  "deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json",
  "deepwiki_briefs/002-bsc-0x5555555555555555555555555555555555555555.json",
  "deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json"
]
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