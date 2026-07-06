<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_2e140cfd-47c3-46a3-b585-6654d84d966f?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The contract address `0x28e2ea090877bf75740558f6bfb36a5ffee9e9df` has no presence in the repository — no source, no ABI, no selectors, no deployer, no transaction history. The scoring reasons confirm this is a pure signal-based flag (`hidden_high_value_contract`, `unknown_verification_status`, `unfamiliar_contract`) with zero code-level evidence. The `next_action: recon_bravo_then_corecritical` is the scoring engine's fallback path when no specific risk-surface tags match. [1](#0-0) [2](#0-1) 

Per the hard rules, this is `NEEDS_LIVE_CONTEXT`: interesting value at risk, but every exploitability gate is blocked by missing source/selector/proxy data.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "name": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified BSC contract holding ~$17.8M TVL with no known protocol identity, no verified source, no deployer attribution, and no transaction history in scope. The combination of fresh_contract_large_balance and hidden_high_value_contract tags on an unverified contract at this value level is a high-priority recon surface. No exploit path can be formed without bytecode, selectors, or source.",
  "live_context_required": [
    {
      "name": "bytecode_and_selectors",
      "reason": "Contract is unverified. Bytecode must be fetched and decompiled (e.g., via Heimdall, Panoramix, or 4byte.directory) to enumerate public selectors and identify value-moving functions before any exploit hypothesis is possible.",
      "command_or_source": "cast code 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df --rpc-url $BSC_RPC | heimdall decompile --stdin"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Contract may be a proxy (EIP-1967, EIP-897, or custom). If so, the implementation address holds the actual logic and may have been recently changed, which is a high-risk signal.",
      "command_or_source": "cast storage 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $17.8M TVL is composed of unknown assets. Identifying which tokens (stablecoins, LP tokens, native BNB) are held determines whether extraction is via ERC-20 transfer, native withdrawal, or share redemption.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "transaction_history",
      "reason": "No volume in 24h but large balance suggests either a dormant escrow, a vesting/lock contract, or a recently funded contract awaiting interaction. Tx history reveals deposit patterns, caller addresses, and which selectors have been exercised.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&sort=desc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "deployer_address_and_funding_path",
      "reason": "Deployer is unknown. Tracing the deployer reveals whether this is a rug-redeploy cluster, a known protocol's internal contract, or a novel attacker-controlled escrow. Funding path may reveal cluster membership.",
      "command_or_source": "cast receipt $(cast tx-hash-from-creation 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df --rpc-url $BSC_RPC) --rpc-url $BSC_RPC | grep 'from'"
    },
    {
      "name": "access_control_on_value_selectors",
      "reason": "Once selectors are known, each value-moving function (withdraw, claim, redeem, sweep, migrate) must be checked for missing or bypassable access control. This is the primary exploit gate.",
      "command_or_source": "After decompilation: review modifier/require patterns on all selectors that transfer tokens or native value."
    }
  ],
  "suspected_exploit_families": [
    "unauthorized_withdrawal_or_sweep",
    "missing_access_control_on_value_moving_functions",
    "phantom_accounting_shares_without_assets",
    "proxy_implementation_or_storage_mismatch"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not retrieved",
      "evidence": "Contract is unverified (verified_source: null, unknown_verification_status tag). No ABI or selector list is available from the candidate brief or repository.",
      "why_it_matters": "Without selectors, no call sequence can be constructed and no exploit path can be validated. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "At least one public selector exists that moves tokens or native value",
      "That selector lacks caller authentication or has a bypassable guard",
      "Contract holds live withdrawable balance (not time-locked or admin-gated)"
    ],
    "call_sequence": [
      "UNKNOWN — requires decompiled selector list"
    ],
    "expected_gain": "Up to $17,779,108 in tokens or native BNB if an unauthenticated withdrawal or sweep selector exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Decompiled ABI loaded into Foundry interface",
      "Attacker EOA with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "UNKNOWN — depends on decompiled selectors"
    ],
    "expected_assertions": [
      "attacker token balance increases after call",
      "contract token balance decreases by matching amount",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

### Citations

**File:** sentinel/scoring.py (L205-208)
```python
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```

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