<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_c2b06e9d-bc6b-426e-8041-1b07f2eeb2d1?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0xaa390a37006e22b5775a34f2147f81ebd6a63641",
    "name": "0xaa390a37006e22b5775a34f2147f81ebd6a63641",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 116
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with a reported ~$19.5B TVL spike, zero 24h volume, zero liquidity, and no deployer attribution. The immediate balance spike on an unknown, potentially unverified contract with high tx count is a high-priority surface for unauthorized withdrawal or missing access control — but no source code, ABI, selectors, or proxy resolution exist in the current pipeline state to confirm or deny any extraction path. The contradictory tags (verified_source: true alongside unknown_verification_status) make the verification status itself unreliable and must be resolved before any hypothesis can be formed.",
  "live_context_required": [
    {
      "name": "source_code_and_abi",
      "reason": "No source code or ABI is present in the pipeline. The verified_source flag conflicts with the unknown_verification_status tag. Must resolve actual Etherscan verification status and fetch full source or bytecode before any selector analysis is possible.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xaa390a37006e22b5775a34f2147f81ebd6a63641&apikey=<KEY>'"
    },
    {
      "name": "proxy_and_implementation_resolution",
      "reason": "Unknown whether this is a proxy. If it is, the implementation address holds the actual logic and selectors. Storage slot 0 and EIP-1967 slots must be checked.",
      "command_or_source": "cast storage 0xaa390a37006e22b5775a34f2147f81ebd6a63641 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url <ETH_RPC>"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "Deployer address is empty in the brief. Without it, funding cluster analysis and rug-redeploy pattern detection are impossible. The creation transaction must be fetched to identify the deployer and initial funding source.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url <ETH_RPC>) --rpc-url <ETH_RPC>) --rpc-url <ETH_RPC>; alternatively query Etherscan internal txs for contract creation"
    },
    {
      "name": "token_balances_and_asset_composition",
      "reason": "The ~$19.5B TVL figure has no token breakdown. Which tokens, in what amounts, are held must be confirmed. A single large stablecoin or wrapped-ETH balance changes the extraction risk profile entirely.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=tokenlist&address=0xaa390a37006e22b5775a34f2147f81ebd6a63641&apikey=<KEY>'"
    },
    {
      "name": "public_selectors_and_value_moving_functions",
      "reason": "No selectors are known. Without bytecode disassembly or verified source, it is impossible to identify withdraw, redeem, claim, sweep, or release entrypoints accessible to an unprivileged caller.",
      "command_or_source": "cast 4byte-decode <bytecode_selector> or use heimdall/panoramix to decompile: cast code 0xaa390a37006e22b5775a34f2147f81ebd6a63641 --rpc-url <ETH_RPC>"
    },
    {
      "name": "transaction_history_and_interaction_pattern",
      "reason": "high_tx_count tag is present but no transaction data is in the pipeline. Transaction traces reveal whether bots are repeatedly calling the same selectors (a strong signal of a known extraction route) or whether the balance spike is a single large deposit with no outflows.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=txlist&address=0xaa390a37006e22b5775a34f2147f81ebd6a63641&sort=desc&apikey=<KEY>'"
    }
  ],
  "suspected_exploit_families": [],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown",
      "evidence": "No source code, ABI, or bytecode analysis is present in the pipeline for this address. The repository contains no entry for 0xaa390a37006e22b5775a34f2147f81ebd6a63641 in state/ethereum_chain_scanner.json, state/latest_targets.json, state/latest_deepwiki_briefs.json, or any run artifact.",
      "why_it_matters": "Without at least one confirmed public selector that moves value, no exploit family can be mapped and no attacker path hypothesis can be formed. All exploit family and path fields are left empty per hard rules."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [],
    "call_sequence": [],
    "expected_gain": "unknown — cannot be estimated without source code or confirmed selectors"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": []
  },
  "rejection_reason": ""
}
```

**Basis for NEEDS_LIVE_CONTEXT:**

The address `0xaa390a37006e22b5775a34f2147f81ebd6a63641` has **no entry** in any pipeline state file in this repository. [1](#0-0) [2](#0-1) 

The candidate brief itself contains two contradictions that must be resolved before any hypothesis is valid:

1. `verified_source: true` is set, but `unknown_verification_status` is simultaneously present as a tag — the actual Etherscan verification state is ambiguous. [3](#0-2) 
2. `deployer_address` is empty and `funding_cluster_id` is empty, making rug-redeploy and funding-cluster analysis impossible.

Per the hunt plan's evidence requirements, a candidate cannot advance without: live balances confirmed, exact entrypoints that move funds, and an attacker gain calculation. [4](#0-3)  None of those exist here. The `recon_bravo_then_corecritical` next action assigned by the scorer is correct — live recon must precede any proof attempt.

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

**File:** HUNT_PLAN.md (L76-85)
```markdown

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy

```