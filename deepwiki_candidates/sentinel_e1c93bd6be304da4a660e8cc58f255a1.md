<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_34ff71e3-9779-46a0-81ac-dd38fb9a08b6?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

Based on the repository's state files and scoring engine, the contract `0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147` does not appear in any enriched state (`latest_targets.json`, `ethereum_chain_scanner.json`, or `latest_deepwiki_briefs.json`). The scoring engine routes it to `recon_bravo_then_corecritical` — the fallback path used when no specific risk surface tag (vault, bridge, reward pool, approval router, cluster) is matched. [1](#0-0) 

Critically: `verified_source` is `null`, deployer is unknown, no ABI or selectors exist in the pipeline, and `unknown_verification_status` does not trigger the `reverse_engineer_unverified_funded_contract` route (which requires the `unverified_contract` entity type tag). [2](#0-1) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "explorer_snapshot",
    "chain": "ethereum",
    "address": "0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147",
    "name": "0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 98
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with ~$1.146M in stablecoin/token balance and an immediate balance spike. No source code, no ABI, no deployer, and no selectors are available. The balance spike pattern on an unidentified contract with known-asset stablecoin holdings is a credible fund-extraction surface if any public value-moving selector exists, but this cannot be confirmed without bytecode recon.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "No ABI or source is available. Decompiling the bytecode (e.g., via Heimdall, Panoramix, or 4byte.directory matching) is required to enumerate all public selectors and identify any withdraw, sweep, claim, redeem, or transfer-out functions callable by an unprivileged address.",
      "command_or_source": "cast code 0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147 --rpc-url $ETH_RPC | heimdall decompile --stdin"
    },
    {
      "name": "deployer_and_deployment_tx",
      "reason": "Deployer address is empty. The deployment transaction reveals constructor arguments, funding source, and whether the deployer is linked to a known cluster (rug redeploy, closed project). This determines whether cluster-risk scoring tags apply.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) --rpc-url $ETH_RPC) --rpc-url $ETH_RPC; or query Etherscan API: https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags include stablecoin_balance and known_asset_balance but specific token addresses and amounts are not enumerated. Knowing which tokens (USDC, USDT, DAI, etc.) and their exact amounts confirms the value-at-risk composition and whether the contract holds LP tokens, receipt tokens, or raw stablecoins.",
      "command_or_source": "cast call 0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147 'balanceOf(address)' <token_address> --rpc-url $ETH_RPC; or Etherscan token holdings tab"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero volume24h_usd is recorded. Inspecting the last 50-100 transactions reveals whether the contract has been called by external users, whether any value-moving selectors have been exercised, and whether a bot or deployer is the only caller (suggesting a honeypot or staged drain setup).",
      "command_or_source": "https://api.etherscan.io/api?module=account&action=txlist&address=0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147&sort=desc"
    },
    {
      "name": "proxy_slot_check",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If a proxy, the implementation address determines the actual callable logic. A recently changed implementation on a funded proxy is a high-priority exploit surface.",
      "command_or_source": "cast storage 0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $ETH_RPC; cast storage 0x08bfa22bb3e024cdfeb3eca53c0cb93bf59c4147 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $ETH_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_shares_or_debt_without_assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not yet decompiled",
      "evidence": "verified_source is null; no ABI in pipeline state; entity_type is unknown_protocol with unknown_verification_status tag",
      "why_it_matters": "Without selectors, no exploit path can be constructed or rejected. Any verdict beyond NEEDS_LIVE_CONTEXT would be speculation."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "At least one public selector exists that moves tokens out of the contract",
      "The selector does not enforce msg.sender == owner or equivalent access control",
      "The contract holds the ~$1.146M in stablecoins at the time of the call"
    ],
    "call_sequence": [
      "STEP 1 (recon): Decompile bytecode to recover selectors",
      "STEP 2 (recon): Identify any withdraw(address,uint256), sweep(address), claim(), or transfer-out functions with no access guard",
      "STEP 3 (proof): Call the identified selector from an unprivileged EOA on a fork at the current block",
      "STEP 4 (proof): Assert attacker token balance increased and contract balance decreased"
    ],
    "expected_gain": "Up to ~$1,146,164 in stablecoin/token value if an unguarded sweep or withdraw selector exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Ethereum mainnet at the block where the balance spike is confirmed",
      "Populate attacker address with no prior relationship to the contract",
      "Confirm contract token balances via balanceOf calls before the attack sequence"
    ],
    "transaction_sequence": [
      "Call the candidate sweep/withdraw/claim selector from attacker EOA with no prior setup",
      "If selector requires a recipient argument, pass attacker address",
      "Check for revert; if no revert, assert token transfer to attacker"
    ],
    "expected_assertions": [
      "IERC20(stablecoin).balanceOf(attacker) > 0 after call",
      "IERC20(stablecoin).balanceOf(target) == 0 or significantly reduced after call",
      "No privileged role check reverted the call"
    ]
  },
  "rejection_reason": ""
}
```

**Summary of triage decision:**

The contract scores 98 and holds ~$1.146M, but the pipeline has zero enrichment on it — no source, no ABI, no deployer, no selectors, no transaction history. The `recon_bravo_then_corecritical` routing is correct: bytecode decompilation and deployer/transaction recon must happen before any local proof attempt is meaningful. The five `live_context_required` items above are the minimum needed to move this to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE`. [3](#0-2)

### Citations

**File:** sentinel/scoring.py (L102-105)
```python
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
```

**File:** sentinel/scoring.py (L193-194)
```python
    elif is_unverified_contract and value >= min_unverified_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "reverse_engineer_unverified_funded_contract"
```

**File:** sentinel/scoring.py (L205-208)
```python
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```