<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_a46d6456-78a9-41f4-90a6-7f1f8e44b29f?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "explorer_snapshot",
    "chain": "bsc",
    "address": "0xfd5840cd36d94d7229439859c0112a4185bc0255",
    "name": "0xfd5840cd36d94d7229439859c0112a4185bc0255",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified BSC contract tagged token_funded_contract and high_token_balance with no source, no ABI, no deployer, and zero real market metrics. The reported tvl_usd of ~1.4e158 is a data artifact — a raw token balance (likely in wei) passed through without decimal or price conversion. The contract may hold real tokens of unknown denomination and identity. Exploitability cannot be assessed without bytecode or source.",
  "live_context_required": [
    {
      "name": "actual_token_holdings",
      "reason": "The tvl_usd figure is clearly a data artifact (>10^158 USD is physically impossible). Need the actual ERC-20 token address(es) held, their real-world price, and true USD value to determine whether real funds are at risk.",
      "command_or_source": "cast call 0xfd5840cd36d94d7229439859c0112a4185bc0255 'balanceOf(address)' <token> --rpc-url $BSC_RPC  OR  query BscScan token holdings tab for this address"
    },
    {
      "name": "bytecode_and_abi",
      "reason": "verified_source is null and unknown_verification_status is set. Without bytecode or ABI there are zero known selectors — no exploit path can be hypothesized.",
      "command_or_source": "cast code 0xfd5840cd36d94d7229439859c0112a4185bc0255 --rpc-url $BSC_RPC  |  4byte-directory or heimdall decompile for selector recovery"
    },
    {
      "name": "deployer_and_creation_tx",
      "reason": "deployer_address is empty. Deployer identity and creation transaction are needed to assess funding source, cluster membership, and whether this is a rug-redeploy or known-bad actor.",
      "command_or_source": "BscScan contract creation tx: https://bscscan.com/address/0xfd5840cd36d94d7229439859c0112a4185bc0255  OR  cast receipt <creation_tx> --rpc-url $BSC_RPC"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "No proxy tags are present but the contract is unverified. Must confirm whether it is a proxy (EIP-1967 / OpenZeppelin transparent / UUPS) before ruling out implementation-swap risk.",
      "command_or_source": "cast storage 0xfd5840cd36d94d7229439859c0112a4185bc0255 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "recent_transaction_history",
      "reason": "volume24h_usd and liquidity_usd are both zero. Need to confirm whether the contract has had any inbound/outbound value transfers recently, or is dormant/honeypot.",
      "command_or_source": "BscScan internal txs + token transfers: https://bscscan.com/address/0xfd5840cd36d94d7229439859c0112a4185bc0255#tokentxns"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no source or ABI available",
      "evidence": "verified_source: null; unknown_verification_status tag set; no bytecode analysis performed",
      "why_it_matters": "Without selectors we cannot confirm any callable value-moving path. All exploit families above are speculative until bytecode is recovered."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds tokens with real USD value (unconfirmed — tvl_usd figure is a data artifact)",
      "At least one public selector exists that moves, releases, or sweeps token balance",
      "No access control guards that selector"
    ],
    "call_sequence": [
      "1. Recover selectors via bytecode decompilation (heimdall / panoramix)",
      "2. Identify any withdraw(), sweep(), claim(), or transfer()-wrapping function with no msg.sender check",
      "3. Call that selector directly from an unprivileged EOA on a BSC fork"
    ],
    "expected_gain": "Unknown — contingent on real token value and presence of an unguarded drain selector. Cannot quantify without live context."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recovered ABI / selector list from bytecode decompilation",
      "Confirmed real token balance and USD value"
    ],
    "transaction_sequence": [
      "Deploy attacker EOA with no prior interaction with target",
      "Call suspected drain/sweep/withdraw selector",
      "Assert attacker token balance increased and contract balance decreased"
    ],
    "expected_assertions": [
      "attacker.tokenBalance > 0 after call",
      "contract.tokenBalance < pre-call value",
      "No revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

---

**Triage rationale:**

**TVL figure is a data artifact.** The `tvl_usd` of ~1.4×10^158 is physically impossible (exceeds the number of atoms in the observable universe). The scoring engine's `value_at_risk>=10000000` reason fired because the raw token balance integer — almost certainly an unscaled wei amount — was passed directly as a USD figure. [1](#0-0) 

**Score of 93 is inflated by the artifact.** 35 of the 93 points come from that bogus value threshold. The remaining points are tag-based heuristics (`unknown_protocol`, `unfamiliar_contract`, `hidden_high_value_contract`) with no source or selector evidence backing them. [2](#0-1) 

**No source, no selectors, no deployer.** `verified_source: null`, deployer is an empty string, and no ABI is available. The triage schema requires at least selector or source evidence before `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` can be issued. [3](#0-2) 

**NEEDS_LIVE_CONTEXT** is the correct verdict because the `token_funded_contract` and `high_token_balance` tags suggest a real token balance may exist, but every piece of information needed to assess exploitability — actual USD value, bytecode, deployer, proxy status, transaction history — is missing. The hard rule "prefer REJECT over speculation" is satisfied by not escalating further; the contract is not rejected outright because a real funded unverified contract on BSC is a legitimate surface worth one enrichment pass.

### Citations

**File:** sentinel/scoring.py (L24-27)
```python
    if value >= 10_000_000:
        score += 35
        reasons.append(f"value_at_risk>=10000000:{value:.0f}")
    elif value >= 1_000_000:
```

**File:** sentinel/scoring.py (L102-105)
```python
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
```

**File:** sentinel_deepwiki_schema.py (L29-35)
```python
    "source_or_selector_basis": [
        {
            "selector_or_function": "",
            "evidence": "",
            "why_it_matters": "",
        }
    ],
```