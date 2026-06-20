<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_ab11d756-472a-47c2-952d-a95991e977a3?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0x656341ef90b622c6634e0573772ffb7f3669b9f3` does not appear anywhere in the repository — no brief, no run output, no scored entry. The candidate brief supplied has `verified_source: null`, no deployer, no selectors, and no ABI. Without any of those, the gate question cannot be answered. The correct verdict is `NEEDS_LIVE_CONTEXT`.

The $538B "TVL" figure is almost certainly a token-balance artifact (e.g., a custodial or escrow address holding a large ERC-20 position), not a real extractable pool — `fdv_usd`, `liquidity_usd`, and `volume24h_usd` are all zero, which is inconsistent with any live DeFi protocol at that scale. [1](#0-0) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x656341ef90b622c6634e0573772ffb7f3669b9f3",
    "name": "0x656341ef90b622c6634e0573772ffb7f3669b9f3",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh unverified Ethereum contract with a reported token balance near $538B and an immediate balance spike. No source, no deployer, no selectors are known. If the balance is real and the contract exposes any public value-moving selector without access control, fund extraction is possible. The balance figure is likely a token-balance artifact rather than a live DeFi pool, but must be confirmed before rejection.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "No verified source and no ABI are available. Without selectors we cannot identify any public value-moving functions (withdraw, redeem, sweep, claim, transfer, etc.) or assess access control.",
      "command_or_source": "cast code 0x656341ef90b622c6634e0573772ffb7f3669b9f3 --rpc-url $ETH_RPC | heimdall decompile --stdin  OR  use 4byte.directory / Dedaub / Panoramix against the raw bytecode"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "The $538B TVL figure is almost certainly a single large ERC-20 holding rather than a real DeFi pool (FDV=0, liquidity=0, volume=0). Identifying the exact token(s) and amounts determines whether the balance is extractable or is simply a custodial/escrow position.",
      "command_or_source": "cast call <token_address> 'balanceOf(address)(uint256)' 0x656341ef90b622c6634e0573772ffb7f3669b9f3 --rpc-url $ETH_RPC  OR  Etherscan token holdings tab"
    },
    {
      "name": "deployer_and_creation_tx",
      "reason": "Deployer address is empty in the brief. The creation transaction reveals constructor arguments, funding source, and whether this is part of a known cluster or a rug-redeploy pattern.",
      "command_or_source": "Etherscan contract creation tx for 0x656341ef90b622c6634e0573772ffb7f3669b9f3; or cast tx $(cast receipt <creation_tx_hash> --rpc-url $ETH_RPC)"
    },
    {
      "name": "proxy_and_implementation_check",
      "reason": "If the contract is a proxy (EIP-1967, EIP-897, or custom), the implementation address holds the real logic and may have been recently changed, which is a high-risk signal.",
      "command_or_source": "cast storage 0x656341ef90b622c6634e0573772ffb7f3669b9f3 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero 24h volume suggests no recent user interaction, but the balance spike tag implies a recent large inflow. Transaction history reveals whether funds were deposited by a single EOA (custodial) or by many users (pool), and whether any withdrawals have already occurred.",
      "command_or_source": "Etherscan internal txs + ERC-20 transfer events for 0x656341ef90b622c6634e0573772ffb7f3669b9f3; or cast logs --address 0x656341ef90b622c6634e0573772ffb7f3669b9f3 --rpc-url $ETH_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_function",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_shares_without_assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or ABI",
      "evidence": "verified_source is null; no selectors have been extracted from bytecode",
      "why_it_matters": "Cannot assess exploitability without knowing which public functions exist and whether they gate value movement"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes at least one public selector that moves tokens or ETH",
      "That selector lacks caller authentication or uses a bypassable check",
      "The token balance is not locked by a time-lock, multisig, or other external constraint"
    ],
    "call_sequence": [
      "1. Identify public selectors via bytecode decompilation",
      "2. Locate any withdraw/sweep/claim/transfer function with no msg.sender check",
      "3. Call that function with attacker-controlled recipient"
    ],
    "expected_gain": "Unknown until selectors are resolved; upper bound is the token balance (~$538B nominal, real value TBD after token identification)"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Pin fork to a recent Ethereum block where the balance spike is present",
      "Impersonate attacker EOA with no prior interaction with the contract",
      "Confirm token balance of contract before attack"
    ],
    "transaction_sequence": [
      "Call the identified public value-moving selector with attacker address as recipient",
      "Assert token balance of attacker increased",
      "Assert token balance of contract decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker token balance after > attacker token balance before",
      "contract token balance after == 0 (or reduced by attacker gain)",
      "no revert on the call"
    ]
  },
  "rejection_reason": ""
}
```

**Why `NEEDS_LIVE_CONTEXT` and not `REJECT`:** The balance spike on a fresh unverified contract is a genuine signal that warrants bytecode inspection. [2](#0-1)  The candidate cannot be rejected on current evidence because the source is absent — rejection requires ruling out a public value-moving path, which is impossible without selectors. [3](#0-2) 

**Why not `NEEDS_LOCAL_PROOF`:** That verdict requires "enough source, selector, balance, or transaction evidence for a local proof attempt." None of those are present here. [4](#0-3)

### Citations

**File:** HUNT_PLAN.md (L59-67)
```markdown
## Triage Rule

Score only protocols that satisfy at least one of these:

1. user funds are already deposited on-chain
2. there is a live reward pool or claimable emission
3. there is a public withdraw/redeem/claim path
4. the protocol is newly deployed, unverified, or forked from a risky pattern
5. a bot or executor repeatedly reveals the same target path
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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

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