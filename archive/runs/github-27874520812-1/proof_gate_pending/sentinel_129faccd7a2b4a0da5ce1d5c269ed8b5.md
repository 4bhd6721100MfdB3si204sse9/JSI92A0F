<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_094d3592-ef9d-4328-a3a8-7ae32b63793c?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The contract address `0x6e395da41cf9362d30461d49f23fe57849b18498` has no entry anywhere in the repository — no source, no ABI, no selectors, no deployer, and no prior triage data. The `deepwiki_briefs/` directory contains only placeholder addresses, and `state/latest_targets.json` does not include this candidate. [1](#0-0) 

With `verified_source: null`, no deployer, no selectors, and no proxy/implementation state, the hard rules mandate `NEEDS_LIVE_CONTEXT`. [2](#0-1) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "runs/20260615T050621Z/candidates_scored.json (not present — sourced from candidate brief only)",
    "chain": "bsc",
    "address": "0x6e395da41cf9362d30461d49f23fe57849b18498",
    "name": "0x6e395da41cf9362d30461d49f23fe57849b18498",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 113
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with ~$120M token balance, immediate balance spike, no verified source, no known protocol identity, and no deployer attribution. The combination of hidden_high_value_contract + balance_spike + unknown_verification_status on a fresh contract is a high-signal pattern for either a honeypot, a migrator redeploy, or a genuinely undefended value pool. Cannot determine which without bytecode and selector recovery.",
  "live_context_required": [
    {
      "name": "bytecode_and_decompiled_selectors",
      "reason": "verified_source is null; no ABI or function selectors are known. Without selectors, no value-moving path can be identified or ruled out.",
      "command_or_source": "cast code 0x6e395da41cf9362d30461d49f23fe57849b18498 --rpc-url $BSC_RPC | xxd | head -200  # then pipe to heimdall or panoramix for selector recovery"
    },
    {
      "name": "proxy_and_implementation_detection",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If so, the implementation address holds the real logic and may have been recently swapped.",
      "command_or_source": "cast storage 0x6e395da41cf9362d30461d49f23fe57849b18498 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  # EIP-1967 impl slot"
    },
    {
      "name": "token_holdings_breakdown",
      "reason": "TVL is $119.9M but liquidity_usd=0 and volume24h_usd=0. Need to identify which tokens are held, whether they are LP tokens, stablecoins, or protocol-native tokens, and whether they are withdrawable.",
      "command_or_source": "https://api.bscscan.com/api?module=account&action=tokentx&address=0x6e395da41cf9362d30461d49f23fe57849b18498&sort=desc&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "deployer_address_and_funding_chain",
      "reason": "deployer_address is empty in the brief. Deployer identity determines whether this is a rug redeploy, a migrator from a closed cluster, or a novel protocol. Funding source may reveal a known exploit pattern.",
      "command_or_source": "https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x6e395da41cf9362d30461d49f23fe57849b18498&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "recent_transaction_history",
      "reason": "balance_spike + immediate_balance_spike tags require confirmation of when funds arrived, from where, and whether any outbound calls have occurred. Zero volume24h suggests no user interaction — atypical for a live protocol.",
      "command_or_source": "https://api.bscscan.com/api?module=account&action=txlist&address=0x6e395da41cf9362d30461d49f23fe57849b18498&sort=desc&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "admin_and_owner_slot_state",
      "reason": "If the contract has an owner or admin, privileged withdrawal paths may exist. Need to confirm whether owner == deployer, a multisig, or address(0) (renounced).",
      "command_or_source": "cast storage 0x6e395da41cf9362d30461d49f23fe57849b18498 0x0 --rpc-url $BSC_RPC  # slot 0 often holds owner; cross-check with decompiled layout"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized_withdrawal_or_sweep",
    "missing_access_control_on_value_moving_functions",
    "proxy_implementation_or_storage_mismatch",
    "phantom_accounting_shares_without_assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI available",
      "evidence": "verified_source: null; no selector recovery has been performed against this address in the repository",
      "why_it_matters": "Cannot confirm or deny any value-moving path without selectors. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$120M in tokens (confirmed by TVL signal)",
      "At least one public selector exists that moves tokens out of the contract",
      "No access control guards that selector against arbitrary callers"
    ],
    "call_sequence": [
      "UNKNOWN — selector recovery required before any call sequence can be constructed"
    ],
    "expected_gain": "UNKNOWN — contingent on selector recovery and access control analysis"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Recover selectors via heimdall or panoramix against live BSC bytecode",
      "Identify token balances and confirm withdrawable assets",
      "Reconstruct storage layout to find owner/admin slots",
      "Determine proxy shape if applicable and fetch implementation"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot populate until selectors and access control are known"
    ],
    "expected_assertions": [
      "BLOCKED — cannot populate until a concrete value-moving path is identified"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:** The candidate scores 113 and carries ~$120M at risk, which is well above any materiality threshold. However, every field needed to reason about exploitability — source code, selectors, deployer, proxy state, token breakdown — is absent. The `balance_spike` + `fresh_contract` + `unknown_verification_status` cluster is a legitimate high-signal pattern (consistent with migrator redeployments or undefended sweep contracts), but it is equally consistent with a honeypot or a custodial contract with hard-coded owner-only withdrawal. Advancing to `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` requires completing the six live-context items above, starting with bytecode decompilation and deployer tracing.

### Citations

**File:** state/latest_targets.json (L1-10)
```json
{
  "targets": [
    {
      "address": "0x7777777777777777777777777777777777777777",
      "category": "migrator vault",
      "chain": "bsc",
      "label": "New Yield Migrator",
      "liquidity_usd": 90000.0,
      "metadata": {
        "category": "migrator vault",
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