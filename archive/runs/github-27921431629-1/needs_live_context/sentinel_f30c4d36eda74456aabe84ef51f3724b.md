<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_36b60804-0d03-4677-b8e8-2223bfb16a5b?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The address `0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735` has no entry anywhere in the repository — no run artifact, no scored JSON, no foundry target, no brief. The candidate brief is purely from the Sentinel scoring pipeline with no enrichment data attached.

Key observations from the brief and the scoring/tagging logic in the codebase:

- `token_funded_contract` tag means discovery was via ERC20 transfer log, not contract creation — someone sent tokens to this contract. [1](#0-0) 
- `fresh_contract_large_token_balance` + `high_token_balance` + zero `liquidity_usd` + zero `volume24h_usd` + zero `fdv_usd` is a strong phantom-valuation pattern — the $141B figure almost certainly reflects a worthless or unpriced token held by the contract, not real extractable value.
- `verified_source: null` — verification status unknown, no ABI, no selectors, no source.
- No `deployer_address`, no `funding_cluster_id`, no proxy state.
- The scoring reasons include `unfamiliar_contract:12`, `unknown_verification_status:8`, `hidden_high_value_contract:18` — custom tags not present in the standard `score_candidate()` path, indicating this came through an extended enrichment pass with no source resolution. [2](#0-1) 
- `next_action: recon_bravo_then_corecritical` is the fallback route for candidates that pass the value threshold but have no specific surface tag routing them elsewhere. [3](#0-2) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "explorer_snapshot (no enriched artifact in repo)",
    "chain": "bsc",
    "address": "0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735",
    "name": "0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with a reported $141B token balance, unknown verification status, no deployer, no source, and no volume or liquidity. The token_funded_contract tag indicates discovery via ERC20 transfer log. If the held token has any real price and the contract exposes public withdrawal or sweep selectors, unauthorized extraction is possible. The $141B figure is almost certainly a phantom valuation from a worthless or self-issued token, but this must be confirmed on-chain before the candidate can be rejected or escalated.",
  "live_context_required": [
    {
      "name": "Token identity and real price",
      "reason": "The entire $141B TVL figure rests on token balances. The token_funded_contract tag means an ERC20 transfer funded this contract. If the token is self-issued, worthless, or untraded, the value-at-risk collapses to zero and the candidate should be rejected.",
      "command_or_source": "cast call 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 'balanceOf(address)(uint256)' <addr> --rpc-url $BSC_RPC; cast call <token_address> 'symbol()(string)' --rpc-url $BSC_RPC; check token on BSCScan token tracker"
    },
    {
      "name": "Verified source or bytecode disassembly",
      "reason": "No source code is available. Without selectors or ABI, no exploit path can be formed. Need to know if any public function can move, sweep, claim, or redeem value without access control.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735&apikey=KEY'; if unverified: cast code 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 --rpc-url $BSC_RPC | evmdis or heimdall decompile"
    },
    {
      "name": "Deployer address and deployment transaction",
      "reason": "No deployer is recorded. The deployer identity and funding source determine whether this is a rug redeploy, a honeypot, or a legitimate custody contract. Needed to assess cluster risk.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735&apikey=KEY'"
    },
    {
      "name": "Proxy slot check",
      "reason": "Unknown whether this is a proxy. If it is, the implementation may differ from any recovered bytecode and may have been recently changed.",
      "command_or_source": "cast storage 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC; cast storage 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC"
    },
    {
      "name": "Recent transaction calldata for selector recovery",
      "reason": "If unverified, transaction calldata is the only way to recover public selectors and determine which functions have been called and whether any move value.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735&sort=desc&apikey=KEY'"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or sweep (if public value-moving selector exists without access control)",
    "phantom accounting (token balance inflated by worthless self-issued token — value-at-risk may be zero)",
    "missing access control on value-moving functions (unknown until source or selectors recovered)",
    "proxy implementation mismatch (unknown until proxy slots checked)"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no source or ABI available",
      "evidence": "verified_source is null; no transaction calldata recovered in this pass; bytecode not fetched",
      "why_it_matters": "Cannot assess any exploit path without at least one public selector that moves value"
    },
    {
      "selector_or_function": "ERC20 transfer into contract (discovery event)",
      "evidence": "tag token_funded_contract indicates contract was discovered via an incoming ERC20 transfer log, not contract creation",
      "why_it_matters": "Confirms the contract holds at least one ERC20 token; the token identity and price determine whether real value is at risk"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds a token with real market value (not confirmed — likely phantom valuation)",
      "At least one public selector exists that can withdraw, sweep, claim, or transfer tokens to an arbitrary address",
      "No access control or ownership check on that selector"
    ],
    "call_sequence": [
      "1. Confirm token identity and real USD value of holdings",
      "2. Recover public selectors via source verification or bytecode disassembly",
      "3. Identify any withdraw/sweep/claim function callable without msg.sender restriction",
      "4. Call that function from an unprivileged EOA on a BSC fork"
    ],
    "expected_gain": "Unknown — contingent on token having real value and a public extraction path existing; current evidence does not support either assumption"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Confirm token address and real price",
      "Recover ABI or selector list from source or bytecode",
      "Identify at least one value-moving public function",
      "Set up BSC fork at current block"
    ],
    "transaction_sequence": [
      "Call candidate value-moving function from unprivileged address",
      "Assert token balance of attacker address increased",
      "Assert contract token balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker token balance after > 0",
      "contract token balance after < contract token balance before",
      "no revert from access control"
    ]
  },
  "rejection_reason": "Insufficient data to reject or escalate. The $141B TVL figure with zero liquidity, zero volume, and zero FDV is a strong indicator of phantom valuation from a worthless or self-issued token. No source, selectors, deployer, or proxy state are available. All three gate questions (which contract holds funds, which selectors move value, can an unprivileged caller gain more than entitlement) are unanswerable without live RPC and explorer data. Escalate only if live context confirms real token value and a public extraction path."
}
```

### Citations

**File:** sentinel/chain_scanner.py (L459-460)
```python
        if deployment.discovery_source == "erc20_transfer_log":
            tags.append("token_funded_contract")
```

**File:** sentinel/scoring.py (L9-26)
```python
def score_candidate(candidate: Candidate, config: dict[str, Any]) -> ScoredCandidate:
    score = 0
    reasons: list[str] = []
    value = candidate.value_at_risk()
    entity_type = candidate.entity_type.lower().strip() or "protocol"
    is_bot_contract = entity_type == "bot_contract"
    is_unverified_contract = entity_type == "unverified_contract" or candidate.verified_source is False
    is_unknown_protocol = entity_type in {"unknown_protocol", "protocol"}
    tags = set(candidate.tags)

    min_value = float(config.get("min_value_usd", 50_000))
    min_bot_value = float(config.get("min_bot_value_usd", 10_000))
    min_unverified_value = float(config.get("min_unverified_value_usd", 100_000))
    min_spike_value = float(config.get("min_spike_value_usd", 100_000))
    min_cluster_value = float(config.get("min_cluster_value_usd", 50_000))
    if value >= 10_000_000:
        score += 35
        reasons.append(f"value_at_risk>=10000000:{value:.0f}")
```

**File:** sentinel/scoring.py (L203-208)
```python
    elif value >= min_value and score < int(config.get("queue_threshold", 35)):
        next_action = "watch"
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
```