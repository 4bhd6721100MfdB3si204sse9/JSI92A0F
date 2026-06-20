<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_5644a03b-a5a5-4e5e-a4a3-48fb47acfc49?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/bsc-0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d.json",
    "chain": "bsc",
    "address": "0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d",
    "name": "0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract holding ~$14.6M TVL with no deployer attribution, no source code, no protocol identity, and no transaction volume. The combination of hidden_high_value_contract + unknown_verification_status + fresh_contract_large_balance on BSC is a high-signal pattern for either a custody contract with missing access control or a honeypot-adjacent structure. Value at risk is material. Cannot advance to NEEDS_LOCAL_PROOF without at minimum a selector map and deployer trace.",
  "live_context_required": [
    {
      "name": "bytecode_selector_map",
      "reason": "verified_source is null and no selectors are known. Without a selector map we cannot identify any value-moving functions, access control, or exploit surface. This is the single hardest blocker.",
      "command_or_source": "cast code 0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d --rpc-url $BSC_RPC | heimdall decompile --stdin  OR  upload bytecode to dedaub.com/decompile  OR  query 4byte.directory for each 4-byte prefix extracted from the bytecode"
    },
    {
      "name": "deployer_address_and_deployment_tx",
      "reason": "deployer_address is empty. Deployer identity reveals funding origin, prior project history, and whether this matches a known rug-redeploy or closed-project cluster. Required before any funding-cluster hypothesis.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d&apikey=$BSCSCAN_KEY'  OR  cast tx $(cast receipt <deploy_tx> --rpc-url $BSC_RPC)"
    },
    {
      "name": "token_holdings_breakdown",
      "reason": "Tags indicate high_token_balance but the specific tokens, amounts, and whether they are user-deposited LP tokens, stablecoins, or protocol-owned reserves are unknown. This determines whether the TVL is extractable user principal or locked protocol collateral.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "recent_transaction_history",
      "reason": "volume24h_usd is 0.0 but the contract may have had prior inbound deposits. Transaction history reveals whether any public callers have successfully called value-moving functions, and whether bot addresses have repeatedly interacted.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d&sort=desc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "proxy_admin_slot_check",
      "reason": "Without source, the contract may be an EIP-1967 or OpenZeppelin transparent proxy. If so, the implementation address and admin slot must be read to determine whether a live implementation change has exposed new selectors or whether the admin slot is unprotected.",
      "command_or_source": "cast storage 0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  &&  cast storage 0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d 0xb53127684a568b3173ae13b9f8a6016f243e3b8a --rpc-url $BSC_RPC"
    },
    {
      "name": "bscscan_source_verification_status",
      "reason": "unknown_verification_status tag may be stale. If source was recently submitted to BSCScan, it changes the triage path to NEEDS_LOCAL_PROOF immediately.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0xa8acdd81f46633b69acb6ec5c16ee7e00cc8938d&apikey=$BSCSCAN_KEY'"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, unstake, claim, liquidate, release, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selectors available",
      "evidence": "verified_source is null; no ABI, no decompiled output, and no transaction input data provided in the candidate brief",
      "why_it_matters": "Cannot form any concrete exploit hypothesis without at least one value-moving selector. All exploit families above are hypothetical until the selector map is obtained."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Selector map must reveal at least one public or externally callable function that moves tokens or native value",
      "That function must lack a caller-identity check (msg.sender guard, merkle proof, or signature requirement)",
      "The $14.6M TVL must be held directly by this contract address, not by a separate custody contract it merely accounts for"
    ],
    "call_sequence": [
      "UNKNOWN — blocked on selector map"
    ],
    "expected_gain": "UNKNOWN — blocked on selector map and token breakdown; upper bound is ~$14.6M if the full balance is directly withdrawable"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Obtain selector map via bytecode decompilation",
      "Confirm token holdings and amounts via BSCScan token API",
      "Confirm deployer and check for prior closed-project links",
      "Check proxy slots for implementation address"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot specify until selector map is available"
    ],
    "expected_assertions": [
      "BLOCKED — cannot specify until selector map is available"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** The hard rule from `deepwiki_prompts.py` is explicit — use `NEEDS_LIVE_CONTEXT` when "selectors, claimability, or source details are missing." [1](#0-0)  Here every selector-level detail is absent: `verified_source` is `null`, no deployer is recorded, no transaction input data is provided, and no ABI exists. [2](#0-1)  The `HUNT_PLAN.md` evidence requirement explicitly demands "exact entrypoints that move funds or rewards" before a candidate becomes a real target — that evidence is entirely absent here. [3](#0-2)  The $14.6M TVL is a genuine signal that keeps this out of `REJECT`, but without a selector map there is no basis for `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE`. [4](#0-3)

### Citations

**File:** deepwiki_prompts.py (L39-41)
```python
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json (L33-35)
```json
    ],
    "verified_source": false
  },
```

**File:** HUNT_PLAN.md (L77-84)
```markdown
Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy
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