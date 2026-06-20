<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_793d9731-11db-4184-88de-47734a0b956f?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "ethereum",
    "address": "0x4585fe77225b41b697c938b018e2ac67ac5a20c0",
    "live_context_source": "deepwiki_briefs/001-ethereum-0x4585fe77225b41b697c938b018e2ac67ac5a20c0.json",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": false,
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
  "live_preconditions": [],
  "attacker_path": {
    "actor": "unknown — no source, ABI, or selectors recovered",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token breakdown not confirmed",
    "attacker_gain": "unknown — no callable value-moving path identified",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot be evaluated without a function entrypoint"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "All seven hard gates that require a concrete exploit path fail. verified_source is null and entity_type is unknown_protocol — the scoring engine's is_unverified_contract flag evaluated to false (scoring.py line 15: verified_source is False, not None), so the reverse_engineer_unverified_funded_contract branch was never reached and next_action fell through to the default recon_bravo_then_corecritical (scoring.py line 208). No specific risk-pattern tag (proxy_impl_changed, active_reward_pool, bridge_escrow, approval_router, share_asset_imbalance, stale_oracle, cluster tags) was present to trigger any structured action branch. The score of 108 is driven entirely by value-at-risk tier, chain weight, and generic unknown/spike tags — not by any source, selector, or structural evidence. Without source code, bytecode selectors, deployer identity, proxy slot state, token breakdown, or transaction history, no exploit hypothesis can be formed, no preconditions can be confirmed, no call sequence can be specified, and no fork test can be written. The candidate must complete all seven live_context_required steps from the triage output before it can be re-evaluated at this gate. Per HUNT_PLAN.md lines 110-115, a candidate must show an unprivileged attacker, a reproducible path, extraction of user funds or excess rewards, and gain beyond entitlement — none of these are satisfiable from the current brief."
}
```

**Basis for REJECT (not NEEDS\_LOCAL\_PROOF):**

`NEEDS_LOCAL_PROOF` requires that a specific callable path has been identified and only a fork test remains to confirm it. Here, the upstream triage verdict was `NEEDS_LIVE_CONTEXT` — the candidate has not yet cleared the prior stage. There is no selector, no function, no call sequence, and no precondition set to hand to a fork test. Writing a fork test with no entrypoint is not possible.

The three gates that are the hard blockers:

| Gate | Status | Reason |
|---|---|---|
| `exact_code_path_or_selector_exists` | FAIL | `verified_source` is `null`; no bytecode selector recovery performed |
| `live_state_supports_preconditions` | FAIL | No token breakdown, no proxy state, no deployer confirmed |
| `concrete_fund_or_reward_gain` | FAIL | No callable path → no gain calculation possible |

The $56.4M balance signal is real and the candidate is worth pursuing through recon, but it does not pass this gate in its current state. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** sentinel/scoring.py (L15-15)
```python
    is_unverified_contract = entity_type == "unverified_contract" or candidate.verified_source is False
```

**File:** sentinel/scoring.py (L205-208)
```python
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"
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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```