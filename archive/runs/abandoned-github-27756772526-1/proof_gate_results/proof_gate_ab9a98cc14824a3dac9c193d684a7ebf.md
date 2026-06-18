<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_b9d462fa-dace-4adc-9e36-62fb8ef5ca24?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0xf2688fb5b81049dfb7703ada5e770543770612c4",
    "live_context_source": "candidate brief only — no separate live context file provided",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": true,
    "live_state_supports_preconditions": false,
    "unprivileged_attacker": false,
    "attacker_controls_trigger": false,
    "exact_code_path_or_selector_exists": false,
    "concrete_fund_or_reward_gain": false,
    "gain_is_beyond_entitlement": false,
    "not_dos_grief_or_liveness_only": true,
    "not_admin_governance_or_key_compromise": true,
    "not_external_dependency_only": true,
    "not_expected_behavior": true,
    "not_known_duplicate": true
  },
  "live_preconditions": [
    {
      "name": "verified_source_or_decompiled_bytecode",
      "status": "missing",
      "reason": "verified_source is null in the brief; no ABI, selector list, or decompiled output exists. Without this, exact_code_path_or_selector_exists cannot be true and no value-moving entrypoint can be confirmed."
    },
    {
      "name": "confirmed_token_balances",
      "status": "unconfirmed",
      "reason": "Tags assert ~$1.6M in bluechip tokens but no on-chain balance query result is present. The balance figure is a tag-derived estimate, not a verified live snapshot."
    },
    {
      "name": "deployer_and_funding_cluster",
      "status": "missing",
      "reason": "deployer_address is empty. Without deployer identity, rug-redeploy patterns and privileged-caller clusters cannot be ruled out, so unprivileged_attacker cannot be confirmed."
    },
    {
      "name": "proxy_implementation_slot",
      "status": "missing",
      "reason": "EIP-1967 and GnosisSafe proxy slots have not been read. If a proxy exists, the implementation address and any upgrade or sweep path are unknown."
    },
    {
      "name": "public_selectors_from_calldata_or_bytecode",
      "status": "missing",
      "reason": "No 4-byte selectors have been recovered. attacker_controls_trigger requires at least one confirmed public value-moving selector callable without access control."
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "status": "missing",
      "reason": "Zero 24h volume is recorded but no tx list has been fetched. Whether any withdrawal has already occurred, or whether only a privileged deployer has interacted, is unknown."
    }
  ],
  "attacker_path": {
    "actor": "unprivileged external user — unconfirmed",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "bluechip BSC tokens — specific tokens and amounts unconfirmed",
    "attacker_gain": "unknown — no selector or value-moving path confirmed",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot be assessed without source, selector, or entitlement logic"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Five hard gates fail simultaneously: live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, concrete_fund_or_reward_gain, and gain_is_beyond_entitlement are all false. The proof gate cannot advance a candidate to NEEDS_LOCAL_PROOF without at minimum: (1) a confirmed public selector or decompiled value-moving function, (2) a verified live balance, and (3) evidence that the caller requires no privilege. All three are absent. The triage verdict was correctly NEEDS_LIVE_CONTEXT; the six live-context commands listed in the triage output must be executed and their results re-submitted before this candidate can re-enter the proof gate."
}
```

**Gate outcome: REJECT**

The proof gate schema [1](#0-0)  does not include `NEEDS_LIVE_CONTEXT` as a valid verdict — the only options are `REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE`. Because no live context was provided, five hard gates fail and the candidate cannot advance.

The specific blockers, per `HUNT_PLAN.md` evidence requirements [2](#0-1) :

| Hard gate | Status | Blocker |
|---|---|---|
| `live_state_supports_preconditions` | false | No live context file at all |
| `unprivileged_attacker` | false | Deployer unknown; privileged-caller cluster unresolved |
| `attacker_controls_trigger` | false | No selectors recovered |
| `exact_code_path_or_selector_exists` | false | `verified_source` is null, no ABI |
| `concrete_fund_or_reward_gain` | false | Balance is a tag estimate, not a verified query |
| `gain_is_beyond_entitlement` | false | No entitlement logic exists to compare against |

The hard rules in `deepwiki_prompts.py` [3](#0-2)  require preferring REJECT over speculation. The six `live_context_required` commands from the triage output must be executed and their results re-submitted as a live context file before this candidate can re-enter the gate.

### Citations

**File:** sentinel_deepwiki_schema.py (L54-54)
```python
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
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

**File:** deepwiki_prompts.py (L37-42)
```python
- Attacker must be unprivileged.
- Prefer REJECT over speculation.
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
- Reject DoS, griefing, liveness, UX, gas, admin-only, governance-only, leaked-key, malicious oracle owner, and pure third-party dependency issues unless the same path gives attacker-controlled fund/reward gain.
```