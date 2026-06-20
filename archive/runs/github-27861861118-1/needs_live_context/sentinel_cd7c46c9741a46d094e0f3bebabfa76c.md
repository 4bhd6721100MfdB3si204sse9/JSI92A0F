<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_0d8967ee-390f-4ca9-b75e-ea36a74c31ec?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/",
    "chain": "bsc",
    "address": "0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735",
    "name": "0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 113
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract with an immediate balance spike and no deployer or source attribution. The reported $14.1T TVL is almost certainly a data artifact (token balance multiplied by an inflated or manipulated token price given zero liquidity and zero FDV), but the underlying token balance spike on an unverified contract is a real signal. If any portion of the balance is real and the contract exposes public value-moving selectors, an unprivileged caller could drain it. The combination of hidden_high_value_contract + unknown_verification_status + balance_spike on BSC matches the fund-extraction surface.",
  "live_context_required": [
    {
      "name": "token_balance_reality_check",
      "reason": "The $14.1T TVL figure with zero liquidity and zero FDV is a near-certain data artifact. Must identify which token(s) are held, their real market price, and actual USD value before any further work.",
      "command_or_source": "cast call 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 'balanceOf(address)(uint256)' <addr> --rpc-url $BSC_RPC  OR  fetch token transfer events from BscScan API for this address to enumerate held tokens"
    },
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "No source code and no verified selectors. Cannot assess any exploit family without knowing what public functions exist. Need to decompile or 4byte-match the deployed bytecode.",
      "command_or_source": "cast code 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 --rpc-url $BSC_RPC | python3 -c 'import sys; b=bytes.fromhex(sys.stdin.read().strip()[2:]); [print(b[i:i+4].hex()) for i in range(0,len(b)-3) if b[i]==0x63]'  OR  upload bytecode to https://api.openchain.xyz/signature-database/v1/lookup"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "Deployer address is empty. Without it, cannot determine if this is a rug-redeploy, a known-bad cluster, or a legitimate contract. Deployer identity is required to assess access-control assumptions.",
      "command_or_source": "BscScan API: GET https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Unknown whether this is a proxy. If it is, the implementation slot may point to a different contract with different selectors or a recently swapped logic contract.",
      "command_or_source": "cast storage 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  (EIP-1967 impl slot)"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero 24h volume but a balance spike tag implies the funding happened in a single or small number of transactions. Reviewing the tx history reveals whether funds are locked, claimable, or already swept.",
      "command_or_source": "BscScan API: GET https://api.bscscan.com/api?module=account&action=txlist&address=0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735&sort=desc&apikey=$BSCSCAN_KEY"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_sweep_or_withdraw",
    "unauthorized_withdrawal_via_public_selector",
    "phantom_accounting_token_balance_artifact"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not yet extracted",
      "evidence": "verified_source is null; unknown_verification_status tag present; no ABI or selector list available in the brief",
      "why_it_matters": "Cannot confirm or deny the existence of public withdraw/sweep/claim selectors without decompiling the bytecode. This is the single blocking gap for any exploit hypothesis."
    },
    {
      "selector_or_function": "token transfer events (ERC-20 Transfer topic)",
      "evidence": "Tags: token_funded_contract, fresh_contract_large_token_balance, immediate_balance_spike — contract received a large token transfer shortly after deployment",
      "why_it_matters": "Confirms real on-chain token custody. If the token has any real market value, this is the asset at risk. If the token is worthless, the candidate should be rejected as a data artifact."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds tokens with non-trivial real USD value (TVL figure must be verified as non-artifact)",
      "Contract exposes at least one public selector that moves tokens to an arbitrary recipient or to msg.sender",
      "No owner/role check guards that selector"
    ],
    "call_sequence": [
      "1. Confirm real token balance and USD value via RPC",
      "2. Extract selectors from bytecode; match against 4byte database",
      "3. Identify any withdraw(address,uint256), sweep(address), claim(), or transfer-wrapper with no access control",
      "4. Call the selector directly from an unprivileged EOA on a BSC fork",
      "5. Assert token balance of attacker increases and contract balance decreases"
    ],
    "expected_gain": "Unknown until selectors are resolved. If a public drain selector exists and the token balance has real value, gain equals the full contract token balance."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC mainnet at current block",
      "Confirm contract token holdings via balanceOf calls",
      "Load decompiled ABI or manually craft calldata for suspected selectors"
    ],
    "transaction_sequence": [
      "vm.prank(attacker_eoa)",
      "target.call(suspected_drain_selector_calldata)",
      "assertGt(token.balanceOf(attacker_eoa), 0)"
    ],
    "expected_assertions": [
      "attacker token balance increases from zero",
      "contract token balance decreases by the same amount",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale (non-JSON summary):**

The verdict is `NEEDS_LIVE_CONTEXT` for three compounding reasons:

1. **TVL is almost certainly a data artifact.** $14.1T with zero liquidity, zero FDV, and zero 24h volume is the classic signature of a token-balance × inflated-price miscalculation. The `token_funded_contract` + `high_token_balance` tags confirm the balance is in tokens, not native BNB. Real value must be confirmed before any proof work is justified.

2. **Zero source and zero selectors.** `verified_source: null` and `unknown_verification_status` mean there is no ABI, no function list, and no way to identify value-moving paths without bytecode decompilation. The scoring engine's `recon_bravo_then_corecritical` next-action is correct — recon must precede any critical-path work. [1](#0-0) 

3. **No deployer, no cluster.** Both `deployer_address` and `funding_cluster_id` are empty strings, blocking the cluster-risk checks that would elevate this to `NEEDS_LOCAL_PROOF`. [2](#0-1) 

Per the hunt plan's hard stop, a candidate cannot be promoted without a proven unprivileged path and confirmed value at risk. [3](#0-2)  The five live-context items above are the minimum required before a fork test is warranted.

### Citations

**File:** sentinel/scoring.py (L206-208)
```python
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```

**File:** sentinel/scoring.py (L224-232)
```python
def _has_cluster_risk(tags: set[str]) -> bool:
    return bool(
        {
            "prior_project_closed",
            "same_deployer_closed_project",
            "funding_from_closed_project",
            "suspected_rug_redeploy",
        }.intersection(tags)
    )
```

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```