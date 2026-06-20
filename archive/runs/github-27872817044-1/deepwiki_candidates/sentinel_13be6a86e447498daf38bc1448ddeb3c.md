<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_290201e2-6b3e-46b0-8a2e-4123dba2acab?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/012-bsc-0x28e2ea090877bf75740558f6bfb36a5ffee9e9df.json",
    "chain": "bsc",
    "address": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "name": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "$17.85M TVL in an unverified, fresh, hidden BSC contract with no deployer attribution, no source, and no known selectors. The combination of high_native_balance + stablecoin_balance + unknown_verification_status on a fresh contract is a high-signal pattern for either a custody contract with public withdrawal paths or a proxy with a live implementation. Cannot determine exploitability without bytecode and selector data.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "Contract is unverified. No source code or ABI is available. Selectors must be extracted from bytecode via decompiler to identify any public value-moving functions before any hypothesis can be formed.",
      "command_or_source": "cast code 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df --rpc-url $BSC_RPC | heimdall decompile --stdin  # or submit bytecode to Dedaub / 4byte.directory"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags indicate both high_native_balance and stablecoin_balance. Exact token addresses and amounts are needed to understand what assets are at risk and whether they are user deposits or protocol-owned reserves.",
      "command_or_source": "BSCScan token holdings API: https://api.bscscan.com/api?module=account&action=tokenlist&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "deployer_address_and_funding_path",
      "reason": "Deployer field is empty in the brief. Deployer identity and funding source are required to determine if this is a redeploy of a known risky pattern, a closed-project migration, or a novel contract.",
      "command_or_source": "BSCScan creation tx: https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero 24h volume is reported. Need to confirm whether the contract has ever been called, which selectors were invoked, and whether any bot or executor has repeatedly touched it — a key signal for extraction route discovery.",
      "command_or_source": "BSCScan tx list: https://api.bscscan.com/api?module=account&action=txlist&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&sort=desc&apikey=$BSCSCAN_KEY"
    },
    {
      "name": "proxy_implementation_slot_check",
      "reason": "Fresh unverified contracts with large balances are frequently proxy contracts. EIP-1967 and EIP-897 storage slots must be checked to determine if there is a separate implementation with its own selectors and access control.",
      "command_or_source": "cast storage 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC && cast storage 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "proxy or implementation storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or verified source available",
      "evidence": "verified_source is null; tags include unknown_verification_status, audit_hidden_contract, unfamiliar_contract; no URL or deployer address present in candidate brief",
      "why_it_matters": "Without selectors, no concrete call path can be constructed. Bytecode decompilation is the mandatory first step before any exploit hypothesis can be evaluated."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes at least one public selector that moves tokens or native BNB",
      "That selector does not enforce msg.sender == owner or equivalent access control",
      "The $17.85M balance is reachable via that selector without prior deposit or entitlement"
    ],
    "call_sequence": [
      "BLOCKED — requires selector extraction from bytecode before call sequence can be constructed"
    ],
    "expected_gain": "Up to $17.85M in stablecoins and/or native BNB if a public sweep, withdraw, or claim selector exists without access control — entirely unconfirmed pending live context"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC mainnet at current block",
      "Confirm $17.85M balance is present at 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
      "Load decompiled ABI from Heimdall or Dedaub output",
      "Identify any selector matching withdraw / sweep / claim / transfer / rescue patterns"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot construct until selectors are known"
    ],
    "expected_assertions": [
      "BLOCKED — cannot assert until a concrete call path is identified"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate scores 93 and carries ~$17.85M TVL, which clears the value-at-risk threshold by a wide margin. However, every field that would allow a concrete exploit hypothesis is absent:

- `verified_source` is `null` — no source code, no ABI, no selectors
- `deployer_address` is empty — no funding cluster, no redeploy signal
- `volume24h_usd` is `0` — no transaction history to reverse-engineer call patterns
- `liquidity_usd` is `0` — the balance is not in an AMM pool; its custody structure is unknown

Under the hard rules, `NEEDS_LOCAL_PROOF` requires "enough source, selector, balance, or transaction evidence for a local proof attempt." None of those exist here beyond the raw balance figure. `NEEDS_LIVE_CONTEXT` is the correct gate: the candidate is interesting enough to pursue, but the five live-context items above must be resolved before any proof work is meaningful.

The highest-priority retrieval step is **bytecode decompilation** — everything else (proxy check, access control analysis, call sequence construction) is blocked until selectors are known. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** deepwiki_prompts.py (L39-41)
```python
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
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

**File:** sentinel_deepwiki_schema.py (L7-48)
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
```