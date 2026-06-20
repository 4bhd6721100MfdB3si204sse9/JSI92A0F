<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_228450d3-f46f-4ee0-b31b-2a9a7451086a?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8` does not appear anywhere in the repository. The `deepwiki_briefs/` directory contains only three placeholder entries with dummy addresses. No source, ABI, selectors, deployer, proxy state, or transaction data for this contract exists in the codebase.

Based on the full repository context — the `HUNT_PLAN.md` evidence requirements, the `sentinel_deepwiki_schema.py` triage contract, and the fact that `0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8` appears nowhere in the codebase with zero source, selectors, deployer, proxy state, or transaction data — the verdict is `NEEDS_LIVE_CONTEXT`.

The `HUNT_PLAN.md` is explicit: before a candidate becomes a real target, live balances, exact entrypoints, and entitlement calculations must be collected. [1](#0-0)  None of those exist here. The scoring system awarded 18 points specifically for `hidden_high_value_contract` and 8 for `unknown_verification_status`, confirming the high score is driven entirely by opacity, not by any known exploitable surface. [2](#0-1) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/019-bsc-0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8.json",
    "chain": "bsc",
    "address": "0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8",
    "name": "0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified BSC contract holds ~$98.2M in token value with zero verified source, no known deployer, no ABI, and no transaction volume. The entire score is driven by balance opacity (hidden_high_value_contract +18, unknown_verification_status +8, unfamiliar_contract +12). No exploit surface can be assessed without bytecode, selectors, or source.",
  "live_context_required": [
    {
      "name": "verified_source_or_decompiled_bytecode",
      "reason": "verified_source is null and unknown_verification_status is set. Without source or decompiled bytecode no function signatures, access control, or value-moving paths can be identified.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8&apikey={api_key}'; fallback: Dedaub or Panoramix decompile of runtime bytecode"
    },
    {
      "name": "4byte_selector_resolution",
      "reason": "No ABI or selector list is available. Public selectors that move, mint, claim, redeem, release, or sweep value must be identified before any exploit path can be formed.",
      "command_or_source": "cast code 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 --rpc-url {bsc_rpc} | python3 -c 'import sys; b=bytes.fromhex(sys.stdin.read().strip()[2:]); [print(b[i:i+4].hex()) for i in range(0,len(b)-3) if b[i]==0x63]'; cross-reference https://www.4byte.directory"
    },
    {
      "name": "proxy_implementation_slot_check",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy. If a proxy, the implementation address holds the real logic and may have been recently changed while funds remain in old accounting state.",
      "command_or_source": "cast storage 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url {bsc_rpc}; cast storage ... 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url {bsc_rpc}"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "tvl_usd ~$98.2M is attributed to token holdings but the specific tokens, amounts, and whether they are user deposits or protocol-owned reserves are unknown. This determines whether extraction is meaningful.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8&apikey={api_key}'; cross-reference BscScan token holdings tab"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "deployer_address is empty. Identifying the deployer and funding source is required to check for closed-project redeploy patterns, rug-redeploy clusters, or known-unsafe code reuse.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8&sort=asc&apikey={api_key}' | jq '.[0].from'; trace deployer funding via BscScan internal txs"
    },
    {
      "name": "transaction_history_and_interaction_patterns",
      "reason": "volume24h_usd is 0.0 but the contract holds $98M. Zero volume on a large-balance contract is anomalous. Transaction history may reveal deposit patterns, bot interactions, or repeated claim/withdraw attempts that expose the extraction surface.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8&sort=desc&apikey={api_key}'"
    },
    {
      "name": "admin_owner_role_resolution",
      "reason": "If source or decompile reveals an owner/admin slot, determine whether it is an EOA, multisig, or timelock. An EOA admin with public rescue/sweep functions would be a critical escalation signal.",
      "command_or_source": "cast call 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 'owner()(address)' --rpc-url {bsc_rpc}; cast call ... 'admin()(address)' --rpc-url {bsc_rpc}"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_shares_without_assets",
    "proxy_implementation_storage_mismatch"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or verified source",
      "evidence": "verified_source is null; unknown_verification_status tag is set; no selector data exists in the repository or candidate brief",
      "why_it_matters": "Without selectors, no value-moving function can be identified or tested. All exploit families above are hypothetical until bytecode is resolved."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract source or decompiled bytecode must be obtained",
      "At least one public selector that moves, mints, claims, redeems, releases, or sweeps value must exist",
      "The $98.2M token balance must be user deposits or protocol-controlled reserves, not protocol-owned locked tokens with no withdrawal path"
    ],
    "call_sequence": [],
    "expected_gain": "unknown — cannot be estimated without source or selectors"
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

**Key basis for `NEEDS_LIVE_CONTEXT` over `REJECT`:**

The $98.2M TVL is real signal — the scoring system's `hidden_high_value_contract` tag and the `fresh_contract_large_token_balance` tag together indicate a large, recently-funded, unverified contract. [3](#0-2)  Per the hard rules, `REJECT` is reserved for candidates where the issue class is out of scope (DoS, admin-only, etc.) — not for candidates where the surface is simply opaque. The correct gate here is live context collection: bytecode, selectors, deployer trace, and proxy slot check. [1](#0-0)

### Citations

**File:** HUNT_PLAN.md (L59-68)
```markdown
## Triage Rule

Score only protocols that satisfy at least one of these:

1. user funds are already deposited on-chain
2. there is a live reward pool or claimable emission
3. there is a public withdraw/redeem/claim path
4. the protocol is newly deployed, unverified, or forked from a risky pattern
5. a bot or executor repeatedly reveals the same target path

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

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L317-319)
```markdown
- proxy implementation changed while funds remain in old accounting state
- verified source recently changed after deposits
- high-value contracts with only selector-level public usage and no verified ABI
```