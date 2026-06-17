<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_6e73ae8b-6a47-44a4-b30e-ba70072737cf?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

The address `0xf2688fb5b81049dfb7703ada5e770543770612c4` does not appear anywhere in the repository — no existing brief, triage result, or run output. The candidate brief was submitted directly in the prompt. Based on the brief data and the triage rules defined in `sentinel_deepwiki_schema.py` and `HUNT_PLAN.md`, here is the triage output:

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0xf2688fb5b81049dfb7703ada5e770543770612c4",
    "name": "0xf2688fb5b81049dfb7703ada5e770543770612c4",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 45
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$1.6M in bluechip token balances with no verified source, no deployer attribution, no funding cluster, and zero 24h volume. The combination of large known-asset balance and complete absence of source or selector data makes this a high-priority recon target: if any public value-moving selector exists without access control, an unprivileged caller could sweep the held tokens.",
  "live_context_required": [
    {
      "name": "verified_source_or_bytecode",
      "reason": "verified_source is null and no ABI is available. Without source or decompiled bytecode, no selectors, access control, or value-moving paths can be assessed.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0xf2688fb5b81049dfb7703ada5e770543770612c4&apikey=<KEY>' ; cast code 0xf2688fb5b81049dfb7703ada5e770543770612c4 --rpc-url $BSC_RPC | xxd | head -200"
    },
    {
      "name": "deployer_address_and_funding_history",
      "reason": "deployer_address is empty. Deployer identity and funding source are required to assess rug-redeploy patterns, closed-project links, and privileged caller clusters.",
      "command_or_source": "cast tx $(cast logs --from-block earliest --to-block latest --address 0xf2688fb5b81049dfb7703ada5e770543770612c4 --rpc-url $BSC_RPC | head -1 | jq -r .transactionHash) --rpc-url $BSC_RPC | jq .from ; curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf2688fb5b81049dfb7703ada5e770543770612c4&sort=asc&page=1&offset=5&apikey=<KEY>'"
    },
    {
      "name": "proxy_slot_check",
      "reason": "No proxy/implementation state is known. A proxy with a public upgrade or sweep path could expose the full balance to an unprivileged caller.",
      "command_or_source": "cast storage 0xf2688fb5b81049dfb7703ada5e770543770612c4 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC ; cast storage 0xf2688fb5b81049dfb7703ada5e770543770612c4 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balances_breakdown",
      "reason": "Tags indicate bluechip_token_balance and known_asset_balance but the specific tokens and amounts are not enumerated. The exact assets at risk must be confirmed before proof work.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0xf2688fb5b81049dfb7703ada5e770543770612c4&apikey=<KEY>' ; cast balance 0xf2688fb5b81049dfb7703ada5e770543770612c4 --rpc-url $BSC_RPC"
    },
    {
      "name": "public_selectors_from_calldata",
      "reason": "No ABI or selector list is available. Recovering selectors from historical calldata is required to identify any withdraw, claim, sweep, or migrate entrypoints callable by an unprivileged address.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf2688fb5b81049dfb7703ada5e770543770612c4&sort=asc&apikey=<KEY>' | jq '[.result[] | .input[0:10]] | unique' ; cast 4byte-decode <selector> for each recovered 4-byte prefix"
    },
    {
      "name": "recent_transaction_callers_and_patterns",
      "reason": "Zero 24h volume is recorded but the contract holds $1.6M. Understanding who funded it, whether any withdrawals have occurred, and whether a privileged caller has already interacted is essential before assessing unprivileged access.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf2688fb5b81049dfb7703ada5e770543770612c4&sort=desc&page=1&offset=20&apikey=<KEY>'"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, or sweep",
    "proxy, implementation, or storage mismatch that exposes live funds",
    "phantom accounting where shares or debt are created without matching assets"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source",
      "evidence": "verified_source is null; no ABI, selector list, or decompiled output is present in the brief",
      "why_it_matters": "Without selectors, no value-moving path can be confirmed or ruled out. Any public withdraw/sweep/claim function would be the primary exploit surface given the $1.6M balance."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$1.6M in bluechip tokens (confirmed by tags)",
      "At least one public selector exists that moves tokens out of the contract",
      "That selector lacks a caller whitelist, ownership check, or other access gate"
    ],
    "call_sequence": [
      "1. Recover public selectors from calldata or bytecode decompilation",
      "2. Identify any withdraw/sweep/claim/transfer function callable without privilege",
      "3. Call that function with attacker-controlled recipient address",
      "4. Receive bluechip tokens from contract balance"
    ],
    "expected_gain": "Up to ~$1,598,133 in bluechip token value if an unguarded sweep or withdraw selector exists — unconfirmable without source or selector data"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block",
      "Confirm token balances at 0xf2688fb5b81049dfb7703ada5e770543770612c4",
      "Recover and decode all public selectors from bytecode or calldata",
      "Identify any selector that transfers or releases tokens without access control"
    ],
    "transaction_sequence": [
      "vm.prank(attacker) — call the identified unguarded selector with attacker as recipient",
      "Assert attacker token balance increased",
      "Assert contract token balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker.balance(token) > 0 after call",
      "contract.balance(token) < pre-call balance",
      "No revert from access control check"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate is not rejected because the value at risk ($1.6M in bluechip tokens on a fresh, unverified BSC contract) clears the materiality threshold and the `unknown_protocol` + `fresh_contract_large_balance` tag combination is a recognized high-risk pattern in the pipeline.

It cannot be `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` because every critical input is absent: `verified_source` is null, `deployer_address` is empty, `funding_cluster_id` is empty, no selectors are known, and no transaction pattern is available. The hard rules in `deepwiki_prompts.py` require source, selector, balance, or transaction evidence before advancing to local proof. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** deepwiki_prompts.py (L36-42)
```python
## Hard Rules
- Attacker must be unprivileged.
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.
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

**File:** HUNT_PLAN.md (L75-84)
```markdown
## Evidence Required

Before a candidate becomes a real target, collect:

- live balances and claimable amounts
- exact entrypoints that move funds or rewards
- entitlement calculation for a normal user
- attacker gain calculation
- state difference before and after the exploit path
- proof that the gain comes from user funds or reward pool value, not from a separate subsidy
```