<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_793f85fa-6145-4ad9-95a9-d5ad734fa0eb?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

Based on the candidate brief and what the repository's triage schema and hunt rules require, here is the triage verdict. The contract has no verified source, no deployer trace, zero liquidity/volume/FDV, and a $694B TVL figure that is almost certainly a data artifact (raw token balance × stale/incorrect price for an illiquid token). Without source or selectors, no exploit path can be hypothesized with any confidence.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0xdc90f6b111df0c26e349d3cc8d3c357b191e109a",
    "name": "0xdc90f6b111df0c26e349d3cc8d3c357b191e109a",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 108
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified Ethereum contract with a reported ~$694B TVL, immediate balance spike, and no deployer trace. The TVL figure is almost certainly a data artifact (large raw token balance of an illiquid or near-worthless token), but the contract holds real token balances of unknown composition. Without source code or bytecode analysis, no selector or access-control posture is known. If the contract is a poorly-guarded vault, migrator, or sweep target, an unprivileged caller could drain it. The zero liquidity, zero volume, and zero FDV figures make the nominal TVL unreliable and must be verified before any proof work.",
  "live_context_required": [
    {
      "name": "Verified source or decompiled bytecode",
      "reason": "verified_source is null. Without ABI or bytecode, no public selectors, access-control modifiers, or value-moving functions can be identified.",
      "command_or_source": "cast etherscan-source 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a --chain mainnet  OR  cast disassemble $(cast code 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a)"
    },
    {
      "name": "Actual token holdings and real USD value",
      "reason": "tvl_usd=$694B with liquidity_usd=0, volume24h_usd=0, fdv_usd=0 is a strong signal of a data-quality artifact. The real economic value must be confirmed before any proof work is justified.",
      "command_or_source": "cast call <ERC20_TOKEN> 'balanceOf(address)(uint256)' 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a --rpc-url $ETH_RPC  OR  query Etherscan token holdings tab"
    },
    {
      "name": "Proxy / implementation state",
      "reason": "Contract may be a proxy. If a recent implementation upgrade introduced a missing-access-control path, live funds could be at risk.",
      "command_or_source": "cast storage 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "Deployer address and funding cluster",
      "reason": "deployer_address and funding_cluster_id are both empty. Tracing the deployer reveals whether this is a known protocol, a honeypot, or a bot-deployed sweep target.",
      "command_or_source": "cast tx $(cast logs --address 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a --from-block earliest | head -1 | jq -r .transactionHash) --rpc-url $ETH_RPC | grep 'from'"
    },
    {
      "name": "Public function selectors",
      "reason": "Without selectors, no withdraw/redeem/claim/sweep surface can be confirmed. 4byte.directory or Heimdall decompilation needed.",
      "command_or_source": "heimdall decompile 0xdc90f6b111df0c26e349d3cc8d3c357b191e109a  OR  python3 -c \"import requests; [print(requests.get(f'https://www.4byte.directory/api/v1/signatures/?hex_signature={s}').json()) for s in <extracted_selectors>]\""
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting (shares or balances created without matching assets)",
    "proxy or implementation storage mismatch exposing live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source: null; bytecode not fetched in this pass",
      "why_it_matters": "Cannot confirm or deny any exploitable selector without source or decompilation"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds real liquid token value (TVL figure must be verified as non-artifact)",
      "At least one public selector exists that moves tokens without caller validation",
      "No timelock, whitelist, or merkle-proof guard on the value-moving path"
    ],
    "call_sequence": [
      "1. Decompile bytecode to recover public selectors",
      "2. Identify any withdraw(address,uint256), sweep(address), claim(), or redeem() selector with no msg.sender check",
      "3. Call selector with attacker address as recipient on a mainnet fork",
      "4. Assert token balance increase in attacker wallet"
    ],
    "expected_gain": "Unknown — contingent on real token value being confirmed and an unguarded selector existing. Cannot estimate without source."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Confirm real token holdings via balanceOf calls",
      "Decompile bytecode and recover ABI",
      "Identify proxy implementation if applicable",
      "Pin fork block to current mainnet tip"
    ],
    "transaction_sequence": [
      "vm.createSelectFork(ETH_RPC, block.number)",
      "Call any unguarded value-moving selector with address(this) as recipient",
      "Assert IERC20(token).balanceOf(address(this)) > 0"
    ],
    "expected_assertions": [
      "Attacker token balance increases",
      "Contract token balance decreases by matching amount",
      "No revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Key triage rationale:**

- `NEEDS_LIVE_CONTEXT` (not `NEEDS_LOCAL_PROOF`) because the two most critical inputs — verified source/bytecode and confirmed real token value — are both absent. [1](#0-0) 
- The $694B TVL with $0 liquidity, $0 volume, and $0 FDV is a near-certain data artifact. Scoring weight `value_at_risk>=10000000:694332866775` drove the score to 108, but that weight is unreliable until token identity and real price are confirmed. [2](#0-1) 
- Per hard rules, speculation without source, selectors, or confirmed balance is insufficient for `HIGH_CONFIDENCE_CANDIDATE` or `NEEDS_LOCAL_PROOF`. [3](#0-2) 
- The `reverse_engineer_unverified_funded_contract` action defined in `sentinel/targets.py` is the correct next step for this class of candidate. [4](#0-3)

### Citations

**File:** HUNT_PLAN.md (L1-18)
```markdown
# Fund And Reward Extraction Hunt Plan

## Goal

Find protocols where an unprivileged actor can extract user funds or rewards beyond entitlement.

This hunt excludes generic bugs, nuisance liveness issues, and cosmetic failures. The target class is only:

- unauthorized or excessive withdrawal of user principal or pooled value
- reward capture beyond what the actor is entitled to receive

## Gate Question

Use this exact question before escalation:

> Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?

If the answer is not proven against live state or a reproducible fork state, do not promote it.
```

**File:** run_build_deepwiki_briefs.py (L58-97)
```python
    return {
        "schema_version": "sentinel-candidate-brief-v1",
        "rank": rank,
        "candidate": {
            "name": row.get("name", ""),
            "chain": row.get("chain", ""),
            "address": str(row.get("address", "")).lower(),
            "entity_type": row.get("entity_type", "protocol"),
            "category": row.get("category", ""),
            "url": row.get("url", ""),
            "source": row.get("source", ""),
            "external_id": row.get("external_id", ""),
        },
        "score": {
            "value": int(row.get("score", 0) or 0),
            "next_action": action,
            "reasons": reasons,
        },
        "value_at_risk": {
            "usd": value,
            "liquidity_usd": float(row.get("liquidity_usd", 0) or 0),
            "tvl_usd": float(row.get("tvl_usd", 0) or 0),
            "volume24h_usd": float(row.get("volume24h_usd", 0) or 0),
            "fdv_usd": float(row.get("fdv_usd", 0) or 0),
            "price_change_24h_pct": float(row.get("price_change_24h_pct", 0) or 0),
        },
        "live_evidence": {
            "verified_source": row.get("verified_source"),
            "deployer_address": row.get("deployer_address", ""),
            "funding_cluster_id": row.get("funding_cluster_id", ""),
            "tags": list(row.get("tags", [])),
        },
        "deepwiki_focus": {
            "why_this_candidate_matters": _why_it_matters(action, value),
            "proof_route": action,
            "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
            "local_questions": _local_questions(action),
        },
        "raw_scored_row": row,
    }
```

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L172-202)
```markdown
### Stage 5 - DeepWiki Candidate Triage

Copy the MKSIIQO pattern:

- `bot_blueprint.py`
- `bot_runtime.py`
- `deepwiki_triage.py`
- Selenium driver wrapper
- `repositories.json` rotation
- smoke batching

Add Sentinel-specific prompts in a new module:

```text
deepwiki_prompts.py
```

DeepWiki should answer:

```text
Does this live candidate likely expose a concrete unprivileged path to extract funds or rewards beyond entitlement, or should it be rejected before local proof?
```

Routes:

- `REJECT` -> `rejected_by_deepwiki/` only when `SAVE_REJECTED_DEEPWIKI=1`
- `NEEDS_LIVE_CONTEXT` -> `needs_live_context/`
- `NEEDS_LOCAL_PROOF` -> `needs_local_proof/`
- `HIGH_CONFIDENCE_CANDIDATE` -> `deepwiki_candidates/`
- parse failure -> `deepwiki_unknown/`

```

**File:** sentinel/targets.py (L11-12)
```python
    "reward_pool_claimability_check": 1,
    "bridge_escrow_message_validation_check": 2,
```