<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_b9e0ea01-a929-499b-b043-6bab46709619?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0x1715a3e4a142d8b698131108995174f37aeba10d",
    "live_context_source": "sentinel/state/ethereum_chain_scanner.json",
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
  "live_preconditions": [],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "stablecoins (~$14.87M reported by chain-scanner heuristics)",
    "attacker_gain": "UNKNOWN — unquantifiable without confirmed selectors",
    "victim_or_protocol_loss": "UNKNOWN",
    "why_gain_exceeds_entitlement": "UNKNOWN — no source, ABI, or selector data exists to establish entitlement boundary"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "The address 0x1715a3e4a142d8b698131108995174f37aeba10d has no entry in state/ethereum_chain_scanner.json and no verified source anywhere in the repository. The upstream triage verdict was NEEDS_LIVE_CONTEXT, which is not a valid proof-gate input state. The proof gate requires all of the following before any positive verdict can be issued: (1) recovered bytecode selectors identifying at least one public value-moving function, (2) confirmed live preconditions showing that function is callable without privilege, (3) a concrete call sequence with quantified gain, and (4) evidence that the gain exceeds the caller's entitlement. None of these are available. The five hard gates that require code-level or state-level evidence — live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, concrete_fund_or_reward_gain — all fail. The signal profile (large stablecoin balance, balance spike, unverified, Ethereum mainnet) is a legitimate recon target, but signal alone does not satisfy the gate. Promote to NEEDS_LOCAL_PROOF only after bytecode decompilation yields at least one public withdraw/sweep/transfer selector with no msg.sender guard confirmed by static analysis or simulation."
}
```

**Gate rationale against the repository schema:**

The `PROOF_GATE_CONTRACT` schema in [1](#0-0)  accepts only three verdicts: `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. The upstream triage output of `NEEDS_LIVE_CONTEXT` is a `sentinel-triage-v1` verdict and is not a valid input state for this gate.

The address is absent from the live scanner state: [2](#0-1)  contains only placeholder addresses; `0x1715a3e4a142d8b698131108995174f37aeba10d` does not appear anywhere in the file.

The scoring path that produced the candidate's score of 108 relies on tag weights such as `unknown_protocol_weight`, `unverified_contract_weight`, and `hidden_high_value_contract` heuristics defined in [3](#0-2)  and [4](#0-3) . These are signal weights, not proof. The hard gates `exact_code_path_or_selector_exists`, `live_state_supports_preconditions`, and `concrete_fund_or_reward_gain` all require evidence that does not exist in the repository or the brief. Until bytecode decompilation produces at least one confirmed public value-moving selector, the gate cannot pass.

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** state/ethereum_chain_scanner.json (L1-30)
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
      "last_value_usd": 240000.0,
      "max_value_usd": 240000.0,
      "tags": [
        "fresh_contract_large_balance",
        "fresh_contract_large_token_balance",
        "high_token_balance",
        "high_total_balance",
        "token_funded_contract",
        "unknown_protocol",
        "vault_exchange_rate"
      ],
      "token_addresses": [
        "0x8888888888888888888888888888888888888888"
      ],
      "updated_at_block": 100
    },
    "0x3434343434343434343434343434343434343434": {
      "created_at_ms": null,
      "deployer": "",
      "deployment_tx": "0xtransfer02",
```

**File:** sentinel/scoring.py (L44-47)
```python
    if is_unverified_contract:
        unverified_weight = int(config.get("unverified_contract_weight", 20))
        score += unverified_weight
        reasons.append(f"unverified_contract:{unverified_weight}")
```

**File:** sentinel/scoring.py (L102-105)
```python
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
```