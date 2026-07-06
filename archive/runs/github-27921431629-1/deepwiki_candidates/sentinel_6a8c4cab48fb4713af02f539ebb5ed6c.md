<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_6d8373f3-e0e9-4ccc-94e9-bcd7ac4c70c1?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The contract address `0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b` does not appear anywhere in the repository's state files, run outputs, or deepwiki briefs — it is not a previously processed candidate. The triage below is based entirely on the candidate brief provided and the scoring/routing logic in `sentinel/scoring.py`.

The scoring engine's default fallthrough path assigns `recon_bravo_then_corecritical` when no specific surface tag (proxy change, reward pool, bridge escrow, vault share, etc.) is present and the candidate is not a bot or unverified contract in the strict sense — which matches the score of 93 and the `next_action` in the brief. [1](#0-0) 

With `verified_source: null`, no deployer, no ABI, no selector list, and no transaction history, no exploit hypothesis can be formed. The correct verdict is `NEEDS_LIVE_CONTEXT`.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "explorer_snapshot",
    "chain": "bsc",
    "address": "0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b",
    "name": "0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract holding ~$543M in token value with no known protocol identity, no verified source, no deployer attribution, and no transaction history. The combination of hidden_high_value_contract + unknown_verification_status + fresh_contract_large_token_balance at this scale is the highest-priority unresolved surface in the triage queue. No exploit family can be confirmed without bytecode, selectors, or proxy state.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "Source is unverified (verified_source: null). Bytecode must be fetched and decompiled to recover public selectors, function signatures, and storage layout before any value-moving path can be identified.",
      "command_or_source": "cast code 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b --rpc-url $BSC_RPC | python3 -c 'import sys; b=sys.stdin.read().strip(); print([b[i:i+8] for i in range(2,len(b),2) if b[i-2:i]==\"63\" or True])' ; # then run against 4byte.directory or heimdall-rs for decompilation"
    },
    {
      "name": "proxy_slot_check",
      "reason": "Contract may be an EIP-1967 or custom proxy. If an implementation slot resolves to a non-zero address, the real logic and selectors are in the implementation, not this address. Admin slot also needed to assess upgradeability risk.",
      "command_or_source": "cast storage 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC && cast storage 0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $543M TVL is token-denominated (tvl_usd > 0, fdv_usd = 0, liquidity_usd = 0). The specific tokens held determine which asset-moving selectors matter (e.g., ERC-20 transfer, withdraw, redeem). BscScan token holdings API or cast calls against known large-cap token contracts are needed.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "transaction_history_and_deployer",
      "reason": "deployer_address is empty in the brief. Deployer identity and funding source are critical for cluster risk assessment. Transaction history reveals whether the contract has been called, by whom, and whether any value-moving selectors have been exercised.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&sort=asc&apikey=$BSCSCAN_KEY' ; curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "bscscan_source_verification_attempt",
      "reason": "verified_source is null (not false — meaning verification status was not resolved, not that it was checked and failed). A direct BscScan source API call may return verified source or ABI that was missed by the snapshot.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0xf07f1760ade617c4f6c71bd7914bc6bd92e5899b&apikey=$BSCSCAN_KEY'"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting (shares or debt without matching assets)",
    "proxy or implementation mismatch exposing live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or ABI",
      "evidence": "verified_source: null; no ABI in candidate payload; no prior transaction data available in brief",
      "why_it_matters": "Without selectors, no call sequence can be constructed and no exploit family can be confirmed. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Bytecode and selectors must be recovered",
      "At least one public selector must move tokens out of the contract without caller restriction",
      "Contract must not require a privileged role or ownership check on the value-moving path"
    ],
    "call_sequence": [
      "UNKNOWN — pending selector extraction and decompilation"
    ],
    "expected_gain": "UNKNOWN — pending token balance breakdown and selector analysis; potential upper bound ~$543M if a public sweep or withdraw selector exists without access control"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recover selectors from bytecode via heimdall-rs or panoramix",
      "Identify token holdings via BscScan token list",
      "Resolve proxy implementation if applicable"
    ],
    "transaction_sequence": [
      "PENDING — cannot be specified until selectors are known"
    ],
    "expected_assertions": [
      "PENDING — cannot be specified until value-moving path is identified"
    ]
  },
  "rejection_reason": ""
}
```

**Why not REJECT:** The value at risk (~$543M) is real and token-denominated. The tags `hidden_high_value_contract` + `fresh_contract_large_token_balance` + `unknown_verification_status` are exactly the pattern the scoring engine weights most heavily. [2](#0-1) 

**Why not NEEDS_LOCAL_PROOF or HIGH_CONFIDENCE_CANDIDATE:** Zero selectors, zero source, zero deployer, zero transaction history. The hard gates for `NEEDS_LOCAL_PROOF` require at least a code path or selector with evidence — none exists here. [3](#0-2)

### Citations

**File:** sentinel/scoring.py (L24-26)
```python
    if value >= 10_000_000:
        score += 35
        reasons.append(f"value_at_risk>=10000000:{value:.0f}")
```

**File:** sentinel/scoring.py (L201-208)
```python
    elif mainstream_source and value >= mainstream_value and not fresh_or_launch:
        next_action = "watch_mainstream"
    elif value >= min_value and score < int(config.get("queue_threshold", 35)):
        next_action = "watch"
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```

**File:** sentinel_deepwiki_schema.py (L66-78)
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
```