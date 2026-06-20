<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_91571e6e-b00e-4e4c-94f2-d3c462f44f8f?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The repository contains no source, ABI, selector list, deployer trace, or prior triage record for `0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd`. Every field that would support a concrete exploit hypothesis — verified source, proxy implementation, callable selectors, deployer identity, funding cluster — is absent or null in the candidate brief. The correct verdict under the hard rules is `NEEDS_LIVE_CONTEXT`.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd",
    "name": "0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 89
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified Ethereum contract holding ~$311K in token value with an immediate balance spike and no known protocol identity. The combination of hidden_high_value_contract, balance_spike, and unknown_verification_status tags places it squarely in the fund-extraction surface. No source, ABI, or deployer data is available in the current brief, so no exploit path can be assessed without live recon.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "verified_source is null and no ABI is present; without selectors we cannot identify any value-moving entrypoints",
      "command_or_source": "cast code 0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd --rpc-url $ETH_RPC | python3 -c 'import sys,evmdasm; [print(i) for i in evmdasm.disassemble(bytes.fromhex(sys.stdin.read().strip()[2:]))]' ; cast 4byte-decode <selector> for each PUSH4"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Contract may be an EIP-1967 or EIP-897 proxy; implementation address determines the real code surface",
      "command_or_source": "cast storage 0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "token_balance_composition",
      "reason": "TVL is token-denominated ($311K) but the specific token(s) and whether they are withdrawable by a caller is unknown",
      "command_or_source": "cast call <token_address> 'balanceOf(address)(uint256)' 0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd --rpc-url $ETH_RPC ; check Etherscan token holdings tab"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "deployer_address and funding_cluster_id are both empty; deployer identity can reveal redeployed-rug or closed-project patterns",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) | grep -i 'contractAddress: 0x46d73') --rpc-url $ETH_RPC ; Etherscan internal txs tab for contract creation"
    },
    {
      "name": "transaction_history_and_caller_set",
      "reason": "balance_spike and immediate_balance_spike tags suggest a recent large inflow; identifying the funding tx and any subsequent calls reveals whether a sweep or claim path has already been exercised",
      "command_or_source": "Etherscan: https://etherscan.io/address/0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd#tokentxns and #internaltx"
    },
    {
      "name": "access_control_role_slots",
      "reason": "If selectors include withdraw/claim/sweep, storage slots for owner, admin, or role mappings must be read to determine whether those functions are gated",
      "command_or_source": "cast storage 0x46d73dee442a7ba2c1c6948a1114acbf69d76ccd 0 --rpc-url $ETH_RPC (and slots 1-5); cross-reference with decompiled output"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_sweep_or_withdraw",
    "unauthorized_claim_or_release",
    "proxy_implementation_mismatch_exposing_live_funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or verified source",
      "evidence": "verified_source: null; no selector list in candidate brief or repository",
      "why_it_matters": "Cannot confirm or deny any value-moving entrypoint without decompiling the deployed bytecode"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$311K in tokens (confirmed by TVL field)",
      "At least one public selector exists that moves tokens to an arbitrary recipient OR to msg.sender without entitlement check",
      "No access control gates that selector to a privileged role"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector extraction from bytecode before a concrete sequence can be stated"
    ],
    "expected_gain": "Up to ~$311K in token value if an ungated withdraw/sweep/claim selector exists; exact amount depends on token composition and per-call limits"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Obtain ABI via bytecode decompilation (heimdall-rs, panoramix, or whatsabi)",
      "Confirm token holdings and amounts via balanceOf calls",
      "Identify any proxy implementation and resolve final code",
      "Check deployer and funding source for context on intended use"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot be specified until selectors are known"
    ],
    "expected_assertions": [
      "BLOCKED — cannot be specified until selectors are known"
    ]
  },
  "rejection_reason": ""
}
```

**Basis for `NEEDS_LIVE_CONTEXT` (not `NEEDS_LOCAL_PROOF`):**

The brief supplies zero source-or-selector basis. Every field that the hard rules require before a local proof attempt — verified source, ABI, proxy implementation, deployer identity, funding cluster, callable function list — is absent or null. [1](#0-0)  The `NEEDS_LOCAL_PROOF` tier requires "enough source, selector, balance, or transaction evidence for a local proof attempt"; only the balance evidence is present here. [2](#0-1) 

The six `live_context_required` items above are the minimum recon steps before this candidate can be promoted. If bytecode decompilation reveals an ungated `withdraw`, `sweep`, or `claim` selector with no role check, the candidate should be immediately re-triaged as `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE`. [3](#0-2)

### Citations

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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```