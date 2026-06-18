<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_3dd61144-3eb9-4278-8fde-531c5a380b1c?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/013-bsc-0x6aba0315493b7e6989041c91181337b662fb1b90.json",
    "chain": "bsc",
    "address": "0x6aba0315493b7e6989041c91181337b662fb1b90",
    "name": "0x6aba0315493b7e6989041c91181337b662fb1b90",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 103
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "A fresh, unverified BSC contract with ~$2.96M TVL and an immediate balance spike is a high-priority surface for unauthorized fund extraction. The combination of hidden_high_value_contract, audit_hidden_contract, and unknown_verification_status means no public source review has occurred. The balance spike pattern — funds deposited immediately after deployment — matches known patterns for contracts with missing access control on withdrawal or sweep functions. No selectors, deployer, proxy state, or transaction history are present in the brief to confirm or reject exploitability; live context is required before any proof attempt.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "No source is verified. Bytecode must be fetched and decompiled to recover public function selectors and identify any value-moving entrypoints (withdraw, sweep, claim, redeem, transfer). This is the mandatory first step before any call sequence can be constructed.",
      "command_or_source": "cast code 0x6aba0315493b7e6989041c91181337b662fb1b90 --rpc-url $BSC_RPC > bytecode.hex && heimdall decompile bytecode.hex  # or: panoramix 0x6aba0315493b7e6989041c91181337b662fb1b90 --network bsc  # then match 4-byte prefixes against https://www.4byte.directory/api/v1/signatures/?hex_signature=<selector>"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "Deployer address is empty in the brief. The deployer and the funding source transaction must be identified to assess rug-redeploy cluster risk and to understand whether the balance spike came from a single funder (admin-controlled) or multiple depositors (user funds at risk).",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x6aba0315493b7e6989041c91181337b662fb1b90&apikey=$BSCSCAN_KEY'  # then trace the deployer's prior contracts and funding wallet"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Unknown whether the contract is a proxy. If it is, the implementation address holds the actual logic and selectors. A recently changed implementation on a live-funded proxy is a direct exploit surface.",
      "command_or_source": "cast storage 0x6aba0315493b7e6989041c91181337b662fb1b90 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC && cast storage 0x6aba0315493b7e6989041c91181337b662fb1b90 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $2.96M TVL is attributed to high_native_balance and high_total_balance tags but the exact token composition is unknown. The asset mix determines which transfer paths are relevant and whether a native BNB drain or ERC20 sweep is the higher-value target.",
      "command_or_source": "cast balance 0x6aba0315493b7e6989041c91181337b662fb1b90 --rpc-url $BSC_RPC  # native BNB; then: curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0x6aba0315493b7e6989041c91181337b662fb1b90&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "recent_transaction_history",
      "reason": "No transaction patterns are in the brief. Recent calls must be inspected to determine whether any public selectors have already been exercised, whether an owner/admin has interacted post-deployment, and whether the balance spike came from one funding transaction or many depositors.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x6aba0315493b7e6989041c91181337b662fb1b90&sort=asc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "owner_or_admin_slot_check",
      "reason": "If the contract has an owner or admin role stored in a known slot, reading it reveals whether access control is live, zeroed out, or set to a known bad actor. A zero-address owner makes any onlyOwner modifier trivially bypassable.",
      "command_or_source": "cast storage 0x6aba0315493b7e6989041c91181337b662fb1b90 0x0 --rpc-url $BSC_RPC && cast storage 0x6aba0315493b7e6989041c91181337b662fb1b90 0x1 --rpc-url $BSC_RPC && cast storage 0x6aba0315493b7e6989041c91181337b662fb1b90 0x2 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "unauthorized_withdrawal_or_sweep",
    "proxy_implementation_mismatch_exposing_live_funds",
    "phantom_accounting_hidden_admin_backdoor"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or recovered selectors",
      "evidence": "verified_source is null; unknown_verification_status tag present; no ABI or bytecode analysis included in brief",
      "why_it_matters": "Without selectors, no call sequence can be constructed. Bytecode recovery via heimdall or panoramix is the mandatory first step before any proof attempt can be scoped."
    },
    {
      "selector_or_function": "balance_spike / immediate_balance_spike / fresh_contract_large_balance tags",
      "evidence": "Tags indicate funds arrived immediately after deployment. This pattern is consistent with a contract designed to receive and hold funds that may have a public or weakly-guarded withdrawal path.",
      "why_it_matters": "If a public withdraw() or sweep() selector exists with no caller restriction, the entire balance is extractable by any caller in a single transaction."
    },
    {
      "selector_or_function": "high_native_balance tag",
      "evidence": "Contract holds significant native BNB in addition to tokens per the high_native_balance and high_total_balance tags.",
      "why_it_matters": "Native balance withdrawal paths (e.g., a public withdrawBNB() or a fallback-triggered drain) are simpler to exploit than ERC20 paths because they require no token approval mechanics."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes a public or externally callable value-moving function (withdraw, sweep, claim, or transfer) with no msg.sender restriction",
      "OR contract is a proxy whose implementation was recently changed to one containing a backdoor selector",
      "OR owner slot is set to the zero address, making any onlyOwner modifier bypassable by any caller"
    ],
    "call_sequence": [
      "1. Fetch bytecode: cast code 0x6aba0315493b7e6989041c91181337b662fb1b90 --rpc-url $BSC_RPC",
      "2. Decompile with heimdall or panoramix to extract public selectors",
      "3. Match 4-byte prefixes against 4byte.directory to identify withdraw/sweep/claim candidates",
      "4. Call the identified selector with attacker address as recipient (if parameterized) from an unprivileged EOA",
      "5. Confirm balance transfer to attacker address"
    ],
    "expected_gain": "Up to ~$2,964,794 in BNB and/or tokens held by the contract if a public value-moving selector with no access control exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BLOCKED: selector recovery must complete before a fork test can be written",
      "Once selectors are known: fork BSC mainnet at current block with --fork-url $BSC_RPC",
      "Confirm live balance with cast balance and token list before running test",
      "Impersonate a fresh attacker EOA with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "PENDING selector recovery — transaction sequence cannot be specified until bytecode is decompiled and a value-moving selector is identified"
    ],
    "expected_assertions": [
      "PENDING selector recovery — assert attacker token/BNB balance increases by at least the contract's pre-call balance after the identified call"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** `NEEDS_LIVE_CONTEXT` — not `REJECT` because the signal profile (score 103, ~$2.96M TVL, `immediate_balance_spike`, `hidden_high_value_contract`, `audit_hidden_contract`, fresh BSC contract, unknown verification) is a genuine high-priority surface matching the fund-extraction scope. Not `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because zero selectors, no source, no deployer, no proxy state, and no transaction history are present — the hard gate `exact_code_path_or_selector_exists` cannot be satisfied without bytecode recovery first. The six `live_context_required` items above are the minimum needed to promote this to `NEEDS_LOCAL_PROOF`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** deepwiki_prompts.py (L39-41)
```python
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
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

**File:** PLAN.md (L106-112)
```markdown
Unverified funded contract signals:

- verified source is false or missing
- native/token balances exceed `min_unverified_value_usd`
- high-value deposits into contract shortly after deployment
- proxy-like storage or delegatecall behavior without verified implementation
- privileged caller or owner activity before/after deposits
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