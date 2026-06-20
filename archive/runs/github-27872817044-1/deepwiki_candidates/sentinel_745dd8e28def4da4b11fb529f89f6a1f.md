<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_40b9b831-b9f4-4df8-bf71-0a7686b8001a?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

Based on the candidate brief and the Protocol Sentinel codebase, here is the triage output:

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs (not yet materialized)",
    "chain": "bsc",
    "address": "0x172fcd41e0913e95784454622d1c3724f546f849",
    "name": "0x172fcd41e0913e95784454622d1c3724f546f849",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract holding ~$11.5M in known bluechip tokens with zero 24h volume, no deployer attribution, no verified source, and no visible transaction history. The audit_hidden_contract and hidden_high_value_contract tags indicate deliberate obscurity. The combination of large known-asset balance and complete absence of source/selector/deployer data makes this a high-priority recon target: if any public value-moving selector exists without access control, the full balance is at risk to an unprivileged caller.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "verified_source is null and unknown_verification_status is set. No ABI, no function signatures, and no selectors are available. Without decompiled bytecode we cannot identify any value-moving entrypoints (withdraw, sweep, claim, redeem, migrate, etc.) or determine whether access control exists.",
      "command_or_source": "cast code 0x172fcd41e0913e95784454622d1c3724f546f849 --rpc-url $BSC_RPC_URL | python3 -c 'import sys; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b),8) if len(b[i:i+8])==8]' # then resolve via https://www.4byte.directory or run Dedaub/Panoramix decompiler"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "unknown_verification_status combined with a large balance raises the possibility of a proxy with a live or recently swapped implementation. A storage slot mismatch or uninitialized implementation could expose a direct drain path.",
      "command_or_source": "cast storage 0x172fcd41e0913e95784454622d1c3724f546f849 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC_URL  # EIP-1967 impl slot; also check 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f (OpenZeppelin legacy)"
    },
    {
      "name": "deployer_address_and_creation_tx",
      "reason": "deployer_address is empty in the brief. The deployer identity and funding source are required to determine whether this is a redeploy from a closed project, a rug pattern, or a legitimate protocol. Without this, cluster-risk scoring cannot be applied.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x172fcd41e0913e95784454622d1c3724f546f849&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "bluechip_token_balance and known_asset_balance tags confirm the $11.5M TVL is in recognized tokens, but the specific assets (USDT, USDC, WBNB, CAKE, etc.) and their amounts are unknown. The asset mix determines which withdrawal paths are highest-value and whether any single token dominates the balance.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0x172fcd41e0913e95784454622d1c3724f546f849&sort=desc&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "full_transaction_history",
      "reason": "volume24h_usd is 0.0, meaning no recent swap/DEX activity, but internal or direct contract calls may exist. Transaction history reveals which selectors have been called, whether any privileged setup calls were made post-deployment, and whether a bot or EOA has been probing the contract.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x172fcd41e0913e95784454622d1c3724f546f849&sort=asc&apikey=$BSCSCAN_API_KEY'"
    },
    {
      "name": "contract_creation_block_and_age",
      "reason": "created_at_ms is null. fresh_contract_large_balance tag implies recent deployment, but the exact age is unknown. A contract funded immediately after deployment with no subsequent user interaction is a strong indicator of a custodial or sweep-ready contract.",
      "command_or_source": "cast block --rpc-url $BSC_RPC_URL $(cast receipt $(curl -s 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x172fcd41e0913e95784454622d1c3724f546f849&apikey=$BSCSCAN_API_KEY' | jq -r '.result[0].txHash') | grep blockNumber)"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "proxy implementation or storage mismatch that exposes live funds",
    "phantom accounting where shares or debt are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no source or ABI available",
      "evidence": "verified_source is null; unknown_verification_status tag is set; no URL is present in the brief",
      "why_it_matters": "Without selectors we cannot confirm or deny the existence of any public value-moving function. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    },
    {
      "selector_or_function": "inferred sweep/withdraw surface (unconfirmed)",
      "evidence": "audit_hidden_contract + hidden_high_value_contract + fresh_contract_large_balance + zero volume. A contract with $11.5M in bluechip tokens and no DEX activity is not a trading contract; it is most likely a custody, vault, or distribution contract with direct call entrypoints.",
      "why_it_matters": "If a public sweep(), withdraw(), or claim() selector exists without an ownership or whitelist check, an unprivileged caller could drain the full balance. This hypothesis cannot be confirmed without bytecode."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$11.5M in known tokens (confirmed by tags)",
      "At least one public selector exists that moves tokens out of the contract",
      "That selector lacks msg.sender access control or whitelist enforcement"
    ],
    "call_sequence": [
      "1. Decompile bytecode to enumerate public 4-byte selectors",
      "2. Identify any selector matching withdraw/sweep/claim/redeem/release/migrate patterns",
      "3. Call the selector from an unprivileged EOA on a BSC fork pinned to current block",
      "4. Observe token balance delta on the contract and the attacker address"
    ],
    "expected_gain": "Up to $11,522,213 in bluechip tokens if an unguarded sweep or withdraw selector exists. Actual gain depends on which selectors are present and what, if any, access control is enforced."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block via $BSC_RPC_URL",
      "Decompiled ABI from bytecode (Dedaub or Panoramix output)",
      "Attacker address: any unprivileged EOA with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "Identify candidate selectors from decompiled bytecode",
      "For each value-moving selector: call it from attacker EOA with plausible arguments (address(attacker), max uint256, etc.)",
      "Check token balances before and after each call"
    ],
    "expected_assertions": [
      "attacker token balance after > attacker token balance before",
      "contract token balance after < contract token balance before",
      "no revert due to access control or ownership check"
    ]
  },
  "rejection_reason": ""
}
```

---

**Triage rationale:**

The contract is not rejected because the value at risk ($11.5M in bluechip tokens) is real and confirmed by multiple independent tags. It is not advanced to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because every piece of information needed to form a concrete exploit hypothesis is missing:

| Required | Status |
|---|---|
| Verified source or bytecode selectors | **Missing** — `verified_source: null` |
| Deployer address | **Missing** — empty string |
| Funding cluster / creation tx | **Missing** — `created_at_ms: null` |
| Transaction history | **Missing** — `volume24h_usd: 0.0` |
| Proxy/implementation state | **Unknown** |

The scoring engine's fallback path `recon_bravo_then_corecritical` is assigned precisely because none of the specific risk-pattern tags (`proxy_impl_changed`, `active_reward_pool`, `bridge_escrow`, `approval_router`, `share_asset_imbalance`, `suspected_rug_redeploy`, etc.) are present. [1](#0-0)  The `audit_hidden_contract` and `hidden_high_value_contract` tags are heuristic signals, not confirmed exploit surfaces. [2](#0-1) 

Per the hard rules in `HUNT_PLAN.md`, a candidate requires live balances, exact entrypoints, and a reproducible extraction path before escalation. [3](#0-2)  None of those exist here yet. The six `live_context_required` items above are the minimum needed to move this to `NEEDS_LOCAL_PROOF`.

### Citations

**File:** sentinel/scoring.py (L102-105)
```python
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
```

**File:** sentinel/scoring.py (L179-208)
```python
    if _has_proxy_change_live_funds(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "proxy_change_live_funds"
    elif _has_reward_pool_claimability(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "reward_pool_claimability_check"
    elif _has_bridge_escrow_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "bridge_escrow_message_validation_check"
    elif _has_approval_router_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "approval_router_drain_surface"
    elif _has_vault_share_asset_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "vault_share_asset_invariant_check"
    elif _has_lending_oracle_liquidation_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "lending_oracle_liquidation_check"
    elif _has_cluster_risk(tags) and value >= min_cluster_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "investigate_redeploy_funding_cluster"
    elif is_unverified_contract and value >= min_unverified_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "reverse_engineer_unverified_funded_contract"
    elif _has_price_spike(candidate, config) and is_unknown_protocol and value >= min_spike_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "price_spike_recon_then_source_check"
    elif is_bot_contract and value >= min_bot_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "trace_bot_contract_then_target_protocols"
    elif is_bot_contract and value < min_bot_value:
        next_action = "watch_bot_contract"
    elif mainstream_source and value >= mainstream_value and not fresh_or_launch:
        next_action = "watch_mainstream"
    elif value >= min_value and score < int(config.get("queue_threshold", 35)):
        next_action = "watch"
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```

**File:** HUNT_PLAN.md (L77-85)
```markdown
Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy

```