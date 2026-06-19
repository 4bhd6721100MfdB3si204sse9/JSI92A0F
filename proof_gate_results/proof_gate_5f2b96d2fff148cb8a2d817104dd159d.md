<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_2ecaaa2f-1001-451b-a427-8edb6690b1c2?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0xdc90f6b111df0c26e349d3cc8d3c357b191e109a",
    "live_context_source": "candidate_brief_only",
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
    "Verified source or decompiled bytecode must be obtained to identify any public selectors",
    "Real token holdings must be confirmed via on-chain balanceOf calls — reported $694B TVL with $0 liquidity, $0 volume, $0 FDV is a near-certain data artifact",
    "Proxy implementation slot must be checked before any selector analysis",
    "Deployer address must be traced to determine protocol identity and honeypot risk"
  ],
  "attacker_path": {
    "actor": "",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "",
    "attacker_gain": "",
    "victim_or_protocol_loss": "",
    "why_gain_exceeds_entitlement": ""
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "All value-critical hard gates fail. (1) exact_code_path_or_selector_exists=false: no verified source and no decompiled bytecode has been fetched; no public selector, access-control modifier, or value-moving function is known. (2) live_state_supports_preconditions=false: the $694B TVL figure is a data artifact — liquidity_usd=0, volume24h_usd=0, fdv_usd=0 make the nominal value unconfirmable; no on-chain balanceOf call has verified real liquid holdings. (3) attacker_controls_trigger=false: without selectors there is no confirmed callable entrypoint. (4) concrete_fund_or_reward_gain=false and gain_is_beyond_entitlement=false follow directly from (1) and (2). The prior triage verdict was NEEDS_LIVE_CONTEXT, not NEEDS_LOCAL_PROOF; the proof gate requires at minimum confirmed real value and at least one identified selector before local proof work is justified. Promote to NEEDS_LOCAL_PROOF only after: bytecode is decompiled and at least one unguarded value-moving selector is identified, AND on-chain balanceOf confirms non-trivial real token value at the address."
}
```

**Gate rationale summary:**

The proof gate schema (`sentinel_deepwiki_schema.py` L54) only permits `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0)  The prior triage stage correctly routed this to `NEEDS_LIVE_CONTEXT`, but that verdict is not available at the proof gate — and the missing inputs that drove that triage verdict have not been resolved.

Five hard gates fail simultaneously:

| Gate | Status | Reason |
|---|---|---|
| `exact_code_path_or_selector_exists` | false | No source, no decompiled bytecode, no selectors |
| `live_state_supports_preconditions` | false | $694B TVL with $0 liquidity/volume/FDV is a data artifact; no `balanceOf` confirmation |
| `attacker_controls_trigger` | false | No callable entrypoint identified |
| `concrete_fund_or_reward_gain` | false | Follows from above |
| `gain_is_beyond_entitlement` | false | Follows from above |

Per the hard rules in `deepwiki_prompts.py`, speculation without source, selectors, or confirmed balance is insufficient for `NEEDS_LOCAL_PROOF`. [2](#0-1)  The correct next action remains `reverse_engineer_unverified_funded_contract` as identified in the triage pass — re-submit after bytecode decompilation and on-chain balance confirmation. [3](#0-2)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
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

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L222-234)
```markdown
Hard gates:

- current live target only
- unprivileged attacker
- attacker-controlled trigger
- exact code path or selector exists
- concrete fund/reward gain
- gain beyond entitlement
- live state supports the preconditions
- not admin/governance/key compromise
- not DoS/grief/liveness only
- not external dependency only
- not expected behavior or known duplicate
```