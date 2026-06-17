<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_0dc7c0b0-d639-489b-8949-b9e61ffc0600?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

Based on the brief in `deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json` and the triage rules in `HUNT_PLAN.md` and `sentinel_deepwiki_schema.py`:

**Key gaps blocking escalation:**
- `verified_source: true` is set but no source code, ABI, or selectors are present in the brief — the flag only records that on-chain verification exists, not that the content was fetched
- `deployer_address` and `funding_cluster_id` are both empty strings — no cluster or funding-chain analysis is possible
- No proxy status, no admin address, no function list
- The `next_action` assigned by `score_candidate()` is `price_spike_recon_then_source_check` — the scoring engine itself signals that source fetch must happen before any proof work [1](#0-0) [2](#0-1) 

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json",
    "chain": "base",
    "address": "0x6666666666666666666666666666666666666666",
    "name": "Unknown Spike Vault",
    "entity_type": "unknown_protocol",
    "next_action": "price_spike_recon_then_source_check",
    "score": 85
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "A vault-category contract on Base with $185k TVL, 420% 24h price spike, and high transaction count is a credible surface for share-price manipulation, missing access control, or phantom accounting. The spike-plus-unknown-protocol combination is a known precursor pattern for fresh custody surfaces that have not been reviewed. However, no source code, selectors, deployer, or proxy state have been fetched yet, so exploitability cannot be assessed.",
  "live_context_required": [
    {
      "name": "contract_source_and_abi",
      "reason": "verified_source is true but no source code or ABI is present in the brief. Without selectors and function bodies, no exploit path can be formed.",
      "command_or_source": "cast etherscan-source 0x6666666666666666666666666666666666666666 --chain base  OR  fetch from Basescan API: https://api.basescan.org/api?module=contract&action=getsourcecode&address=0x6666666666666666666666666666666666666666"
    },
    {
      "name": "proxy_and_implementation_status",
      "reason": "Vault contracts are frequently proxied. If the implementation was recently changed with live funds present, this is a high-priority escalation path.",
      "command_or_source": "cast storage 0x6666666666666666666666666666666666666666 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url https://mainnet.base.org"
    },
    {
      "name": "live_token_balances",
      "reason": "TVL of $185k is reported but the underlying asset(s) and actual on-chain balance must be confirmed before any proof setup.",
      "command_or_source": "cast call 0x6666666666666666666666666666666666666666 'asset()(address)' --rpc-url https://mainnet.base.org  THEN  cast call <asset> 'balanceOf(address)(uint256)' 0x6666666666666666666666666666666666666666 --rpc-url https://mainnet.base.org"
    },
    {
      "name": "deployer_address_and_funding_cluster",
      "reason": "deployer_address is empty. Deployer identity and funding source are needed to detect rug-redeploy or closed-project migration patterns.",
      "command_or_source": "Fetch contract creation tx from Basescan: https://api.basescan.org/api?module=account&action=txlist&address=0x6666666666666666666666666666666666666666&sort=asc  — first tx is the deploy tx; extract 'from' field."
    },
    {
      "name": "public_value_moving_selectors",
      "reason": "Without a selector list (withdraw, redeem, claim, sweep, migrate, rescue), no call sequence can be constructed for a proof attempt.",
      "command_or_source": "cast 4byte-decode against ABI once source is fetched, or use: https://api.openchain.xyz/signature-database/v1/lookup?function=<selector> for each 4-byte selector found in recent txs to the contract."
    },
    {
      "name": "access_control_on_value_functions",
      "reason": "Missing access control on withdraw/redeem/sweep is the primary exploit family for vault contracts. Must confirm whether these functions check msg.sender against a share balance or owner mapping.",
      "command_or_source": "Review source once fetched; look for onlyOwner / require(msg.sender == ...) guards on withdraw(), redeem(), sweep(), rescue(), emergencyWithdraw()."
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_functions",
    "share_price_or_exchange_rate_drift",
    "phantom_accounting_shares_without_matching_assets",
    "rounding_favoring_attacker_on_repeat_calls"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — source not fetched",
      "evidence": "verified_source: true in brief but no ABI or source body is present. Category is 'vault', which implies ERC-4626 or similar share/asset interface with withdraw() and redeem() entrypoints.",
      "why_it_matters": "If withdraw() or redeem() lack per-share entitlement checks, an unprivileged caller could drain assets beyond their deposited share."
    },
    {
      "selector_or_function": "unknown sweep/rescue/emergencyWithdraw",
      "evidence": "Unknown protocol with no audit history and sudden price spike. Unreviewed vault contracts frequently include admin-callable sweep or rescue functions that lack access control.",
      "why_it_matters": "A public sweep() with no access guard is a direct fund extraction path requiring no preconditions beyond calling it."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract source must be fetched to confirm selector existence",
      "At least one value-moving function must be callable without share ownership or with share-price manipulation",
      "Live TVL ($185k) must remain in the contract at time of proof"
    ],
    "call_sequence": [
      "UNKNOWN — cannot construct without source/ABI"
    ],
    "expected_gain": "Up to $185k in underlying vault assets if a public withdraw/sweep path exists without entitlement check; partial gain if share-price drift or rounding is exploitable over multiple calls"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork Base mainnet at current block",
      "Confirm contract bytecode matches verified source",
      "Identify underlying asset and total assets held",
      "Identify share token and total supply"
    ],
    "transaction_sequence": [
      "BLOCKED — requires source fetch and selector confirmation before sequence can be defined"
    ],
    "expected_assertions": [
      "attacker token balance after > attacker token balance before",
      "attacker gain > any deposited principal (i.e., gain is beyond entitlement)",
      "vault total assets decrease by attacker gain amount"
    ]
  },
  "rejection_reason": ""
}
```

**Summary of decision logic:**

| Signal | Weight |
|---|---|
| Vault category + $185k TVL | Keeps candidate alive |
| 420% price spike + unknown protocol | Elevates priority |
| `verified_source: true` but no source content | Blocks proof work |
| Empty deployer, no URL, no proxy state | Blocks cluster and access-control analysis |
| Scoring engine `next_action` = `price_spike_recon_then_source_check` | Confirms live fetch must precede any proof |

The hard rules from `HUNT_PLAN.md` require "exact entrypoints that move funds" and "attacker gain calculation" before escalation. [3](#0-2)  Neither is available here, so `NEEDS_LIVE_CONTEXT` is the correct gate. [4](#0-3)

### Citations

**File:** sentinel/scoring.py (L195-196)
```python
    elif _has_price_spike(candidate, config) and is_unknown_protocol and value >= min_spike_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "price_spike_recon_then_source_check"
```

**File:** deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json (L31-43)
```json
    "verified_source": true
  },
  "rank": 3,
  "raw_scored_row": {
    "address": "0x6666666666666666666666666666666666666666",
    "category": "vault",
    "chain": "base",
    "created_at_ms": null,
    "deployer_address": "",
    "entity_type": "unknown_protocol",
    "external_id": "base:0x6666666666666666666666666666666666666666",
    "fdv_usd": 0.0,
    "funding_cluster_id": "",
```

**File:** HUNT_PLAN.md (L77-85)
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