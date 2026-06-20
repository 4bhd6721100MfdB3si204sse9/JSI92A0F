<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_4036a0d3-837d-42bc-a0c9-326070806464?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The contract address `0x462b30a53c8552035506e82ce7b6a6c418b0477f` does not appear anywhere in the repository. The `deepwiki_briefs/`, `runs/`, and `foundry_targets/` directories contain only placeholder/example addresses. The only available data is what was supplied in the candidate brief itself.

Applying the triage rules strictly against that brief:

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x462b30a53c8552035506e82ce7b6a6c418b0477f",
    "name": "0x462b30a53c8552035506e82ce7b6a6c418b0477f",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified fresh contract on BSC holding ~$28.6M in stablecoins/tokens with no known protocol identity, no deployer attribution, and no source code. The combination of hidden_high_value_contract + stablecoin_balance + unknown_verification_status on a fresh deployment is a high-priority surface for unauthorized withdrawal or sweep paths. No exploit hypothesis can be formed without selectors or bytecode.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "verified_source is null and no ABI is available. Without selectors we cannot identify any value-moving public functions or determine whether access control exists.",
      "command_or_source": "cast code 0x462b30a53c8552035506e82ce7b6a6c418b0477f --rpc-url $BSC_RPC | python3 -c 'import sys,re; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b)-6,2) if re.match(\"[0-9a-f]{8}\",b[i:i+8])]' | sort -u  # then resolve via https://www.4byte.directory/"
    },
    {
      "name": "decompiled_abi",
      "reason": "Need human-readable function signatures and argument types to assess whether withdraw/redeem/claim/sweep selectors are present and whether they gate on msg.sender.",
      "command_or_source": "Submit bytecode to https://app.dedaub.com/decompile or run: heimdall decompile 0x462b30a53c8552035506e82ce7b6a6c418b0477f --rpc-url $BSC_RPC"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Fresh funded contracts are frequently transparent or UUPS proxies. If a proxy, the implementation address determines the actual logic and may have been recently swapped.",
      "command_or_source": "cast storage 0x462b30a53c8552035506e82ce7b6a6c418b0477f 0x360894a13ba1a3210667c828492db98dca3e2076d785ef654463aef51204902 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags indicate stablecoin_balance and high_token_balance but do not identify which tokens or whether they are withdrawable vs. locked. Specific token addresses determine the actual extractable asset.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0x462b30a53c8552035506e82ce7b6a6c418b0477f&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "deployer_and_funding_source",
      "reason": "deployer_address is empty. Deployer identity and funding path determine whether this is a redeployed rug, a migrator, or a legitimate protocol. Required to assess intent and cluster membership.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x462b30a53c8552035506e82ce7b6a6c418b0477f&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "transaction_history",
      "reason": "volume24h_usd is 0.0 but the contract holds $28.6M. Zero volume on a large-balance fresh contract suggests funds were deposited in bulk with no user interaction — consistent with a custody contract, migrator, or honeypot. Tx history reveals deposit pattern and whether any withdrawals have occurred.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x462b30a53c8552035506e82ce7b6a6c418b0477f&sort=asc&apikey=$BSCSCAN_KEY'"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized_withdrawal_or_sweep",
    "missing_access_control_on_value_moving_function",
    "proxy_implementation_mismatch_exposing_live_funds",
    "phantom_accounting_or_unguarded_claim"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source, no ABI",
      "evidence": "verified_source: null; unknown_verification_status tag present; no URL or protocol name available",
      "why_it_matters": "Cannot confirm or deny the existence of public withdraw/redeem/sweep/claim selectors without bytecode analysis. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes at least one public or external function that transfers token balance to an arbitrary caller-controlled address",
      "No msg.sender allowlist or ownership check guards that function",
      "Contract holds live stablecoin balance (~$28.6M) at time of call"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector extraction and decompilation before a concrete sequence can be constructed"
    ],
    "expected_gain": "Up to $28.6M in stablecoins if an unguarded sweep or withdrawal selector exists; amount depends on which tokens are held and whether the function drains the full balance or a caller-specified amount"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Obtain decompiled ABI and identify candidate value-moving selectors",
      "Pin BSC fork to a block where contract balance is confirmed live",
      "Fund attacker EOA with enough BNB for gas"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot populate until selectors are known"
    ],
    "expected_assertions": [
      "BLOCKED — cannot populate until selectors are known"
    ]
  },
  "rejection_reason": ""
}
```

**Why `NEEDS_LIVE_CONTEXT` and not `NEEDS_LOCAL_PROOF`:**

The candidate has meaningful value at risk ($28.6M stablecoins, BSC, fresh, hidden), which clears the interest threshold. However, `verified_source` is `null`, no ABI or selectors exist in the brief, the deployer field is empty, and `volume24h_usd` is `0.0` despite the large balance. There is no code path, selector, or transaction evidence to anchor a local proof attempt. All six live-context items above must be resolved before this can advance to `NEEDS_LOCAL_PROOF`. [1](#0-0)

### Citations

**File:** sentinel_deepwiki_schema.py (L7-49)
```python
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
```