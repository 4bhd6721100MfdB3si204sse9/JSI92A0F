<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_a78f227c-162f-4161-a40e-8fd9f5c1b19d?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/017-bsc-0x346575fc7f07e6994d76199e41d13dc1575322e1.json",
    "chain": "bsc",
    "address": "0x346575fc7f07e6994d76199e41d13dc1575322e1",
    "name": "0x346575fc7f07e6994d76199e41d13dc1575322e1",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract tagged hidden_high_value_contract with a reported TVL of ~$47B. However, FDV, liquidity, and 24h volume are all zero, which is a strong indicator that the balance figure is driven by illiquid or zero-market tokens rather than real extractable value. No source code, no deployer, no ABI, and no transaction history are available. The contract cannot be dismissed outright because the token-funded pattern on an unverified fresh contract is a known surface for missing-access-control sweep bugs, but no exploit path can be constructed without live context.",
  "live_context_required": [
    {
      "name": "token_holdings_and_real_liquidity",
      "reason": "TVL of ~$47B with $0 FDV, $0 liquidity, and $0 volume is almost certainly a token-balance inflation artifact. Need the actual ERC-20 token list held by the contract, each token's real DEX liquidity, and whether any token has a live price feed that could be drained.",
      "command_or_source": "cast call 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC; bscscan token holdings tab; defillama token liquidity cross-check"
    },
    {
      "name": "bytecode_and_selector_map",
      "reason": "verified_source is null and unknown_verification_status is set. Without ABI or decompiled selectors, no value-moving function can be identified. Need 4-byte selector extraction and decompilation to check for withdraw, claim, sweep, transfer, or redeem paths callable by an unprivileged address.",
      "command_or_source": "cast code 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC | xxd | grep -E '(63[0-9a-f]{8}14)'; heimdall decompile 0x346575fc7f07e6994d76199e41d13dc1575322e1; 4byte.directory lookup"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "deployer_address is empty. The deployer identity and funding source are needed to determine whether this is a redeployed rug, a migrator receiving user funds, or a protocol treasury. Without this, cluster-risk scoring cannot be applied.",
      "command_or_source": "bscscan contract creation tx for 0x346575fc7f07e6994d76199e41d13dc1575322e1; cast tx <creation_tx_hash> --rpc-url $BSC_RPC"
    },
    {
      "name": "transaction_history_and_interaction_pattern",
      "reason": "volume24h_usd is zero and no interaction data is present. Need to confirm whether the contract has ever been called, whether tokens were deposited by users or self-funded by the deployer, and whether any sweep or withdrawal transactions have occurred.",
      "command_or_source": "bscscan internal txs and token transfer tab for 0x346575fc7f07e6994d76199e41d13dc1575322e1; cast logs --address 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC --from-block earliest"
    },
    {
      "name": "proxy_or_implementation_check",
      "reason": "Fresh unverified contracts on BSC with large balances are frequently minimal proxies (EIP-1167) or EIP-1967 transparent proxies pointing to an unverified implementation. If a proxy, the implementation address must be resolved and decompiled separately.",
      "command_or_source": "cast storage 0x346575fc7f07e6994d76199e41d13dc1575322e1 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC; cast storage 0x346575fc7f07e6994d76199e41d13dc1575322e1 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_function",
    "unauthorized_sweep_or_withdraw",
    "phantom_accounting_token_balance_without_matching_real_asset"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source is null; unknown_verification_status tag is set. No ABI, no decompiled output, and no 4-byte selector data are available in the current brief.",
      "why_it_matters": "Without at least one confirmed public selector that moves value, no exploit path can be constructed and no local proof can be scoped. This is the primary blocker for advancing beyond NEEDS_LIVE_CONTEXT."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds tokens with real extractable liquidity (not yet confirmed — FDV and liquidity are both zero)",
      "At least one public selector exists that transfers, redeems, claims, or sweeps tokens without an ownership or whitelist check",
      "No reentrancy guard or per-caller accounting prevents repeated extraction"
    ],
    "call_sequence": [
      "UNKNOWN — selector map required before call sequence can be constructed"
    ],
    "expected_gain": "UNKNOWN — contingent on token liquidity verification and selector discovery"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Resolve actual token holdings and confirm at least one token has real DEX liquidity on BSC",
      "Decompile bytecode and extract all public selectors",
      "Identify any selector that moves tokens without msg.sender validation",
      "Pin BSC fork to a recent block where the contract holds the target balance"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot populate until selector map and token liquidity are confirmed"
    ],
    "expected_assertions": [
      "BLOCKED — cannot populate until attacker path is confirmed"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale (non-JSON summary):**

The single largest signal here is the `$46.96B TVL` paired with `$0 FDV`, `$0 liquidity`, and `$0 volume`. This combination is the canonical BSC token-balance inflation pattern — the contract holds tokens whose price oracle or aggregator reports a large USD value, but those tokens have no real market depth and cannot be sold. If confirmed, the "value at risk" collapses to near zero and the candidate becomes a `REJECT`.

The only path to a higher verdict is live context: decompile the bytecode to find selectors, verify the token holdings against real DEX liquidity, and trace the deployer. If a public sweep/withdraw selector exists and the tokens are genuinely liquid, this escalates immediately to `NEEDS_LOCAL_PROOF`.

Relevant scoring logic that produced the `recon_bravo_then_corecritical` action is the fallback branch in `sentinel/scoring.py` at line 208 — none of the specialized tag checks (`proxy_change_live_funds`, `reward_pool_claimability`, `bridge_escrow`, etc.) matched, so the candidate fell through to the generic high-score path. [1](#0-0)

### Citations

**File:** sentinel/scoring.py (L205-209)
```python
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"

```