<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_0ba168bd-aa14-4f55-afa0-e672613b598e?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/021-bsc-0x92b7807bf19b7dddf89b706143896d05228f3121.json",
    "chain": "bsc",
    "address": "0x92b7807bf19b7dddf89b706143896d05228f3121",
    "name": "0x92b7807bf19b7dddf89b706143896d05228f3121",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$38.3M in stablecoin/token value with no verified source, no known deployer, no recovered selectors, and no proxy/admin state. The combination of hidden_high_value_contract + audit_hidden_contract + unknown_verification_status at this TVL scale makes it a priority recon target. If any public value-moving selector exists without access control, the entire balance is at risk to an unprivileged caller.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_recovery",
      "reason": "No source is verified and no selectors are known. Without the function selector set, no exploit family can be mapped and no call sequence can be formed.",
      "command_or_source": "cast code 0x92b7807bf19b7dddf89b706143896d05228f3121 --rpc-url $BSC_RPC | python3 -c 'import sys,re; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b)-8,2) if re.match(\"[0-9a-f]{8}\",b[i:i+8])]' | sort -u  # then cross-reference with 4byte.directory"
    },
    {
      "name": "proxy_slot_inspection",
      "reason": "Contract may be a proxy (EIP-1967 or EIP-897). If a live implementation was recently swapped, the storage layout or access control may be broken.",
      "command_or_source": "cast storage 0x92b7807bf19b7dddf89b706143896d05228f3121 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  # EIP-1967 impl slot; also check 0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2f for EIP-897"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "Deployer address is missing from the brief. Identifying the deployer and its funding source is required to detect redeploy-cluster patterns, rug-redeploy signals, or privileged-caller clustering.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x92b7807bf19b7dddf89b706143896d05228f3121&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "live_token_balance_breakdown",
      "reason": "Tags indicate stablecoin_balance and high_token_balance but the exact token addresses, amounts, and whether they are user deposits vs. protocol-owned are unknown. This determines the realistic extractable value.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0x92b7807bf19b7dddf89b706143896d05228f3121&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "recent_transaction_history_and_caller_set",
      "reason": "Transaction calldata from recent interactions can reveal function selectors in use, whether callers are EOAs or contracts, and whether any profit-sweep pattern is visible.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x92b7807bf19b7dddf89b706143896d05228f3121&sort=desc&page=1&offset=50&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "source_verification_status",
      "reason": "verified_source is null in the brief. Confirming whether partial ABI or source exists on BSCScan may shortcut selector recovery.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x92b7807bf19b7dddf89b706143896d05228f3121&apikey=$BSCSCAN_KEY'"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, or sweep",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selectors recovered",
      "evidence": "verified_source is null; no ABI, no calldata samples, and no transaction history are present in the brief",
      "why_it_matters": "Without at least one confirmed public selector that moves value, no exploit path can be formed and no local proof can be scoped"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "At least one public selector exists that moves tokens or native value out of the contract",
      "That selector lacks caller authentication or uses a broken access-control check"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector recovery and source or bytecode analysis before a concrete sequence can be stated"
    ],
    "expected_gain": "Up to ~$38.3M in stablecoin or token value if a public sweep/withdraw/claim path exists without access control; exact gain unknown until selectors and entitlement logic are recovered"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block with cast/anvil: anvil --fork-url $BSC_RPC --fork-block-number latest",
      "Confirm contract balance on fork matches live state",
      "Load recovered ABI or raw selectors into the test harness"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot be specified until live_context_required items above are resolved"
    ],
    "expected_assertions": [
      "BLOCKED — cannot be specified until value-moving selectors and entitlement logic are known"
    ]
  },
  "rejection_reason": ""
}
```

**Rationale summary:**

The candidate scores 93 and holds ~$38.3M, which clears the value threshold by a wide margin. The `hidden_high_value_contract` + `audit_hidden_contract` + `unknown_verification_status` tag cluster is the highest-risk combination the scoring engine produces. However, the brief contains **zero** of the minimum evidence required to form an exploit hypothesis:

- No verified source or ABI
- No recovered selectors
- No deployer address
- No proxy/admin state
- No transaction history

Per the hard rules, `NEEDS_LIVE_CONTEXT` is the correct verdict — not `NEEDS_LOCAL_PROOF` — because there is no selector or source basis to scope a fork test. The six `live_context_required` items above are the exact recon steps needed before this can be promoted. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L195-201)
```markdown
Routes:

- `REJECT` -> `rejected_by_deepwiki/` only when `SAVE_REJECTED_DEEPWIKI=1`
- `NEEDS_LIVE_CONTEXT` -> `needs_live_context/`
- `NEEDS_LOCAL_PROOF` -> `needs_local_proof/`
- `HIGH_CONFIDENCE_CANDIDATE` -> `deepwiki_candidates/`
- parse failure -> `deepwiki_unknown/`
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