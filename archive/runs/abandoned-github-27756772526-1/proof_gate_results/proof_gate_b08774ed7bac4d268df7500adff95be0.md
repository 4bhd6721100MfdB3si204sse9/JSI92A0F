<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_f72a3046-2533-4d6e-ad1e-36232bd2f887?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x57cf8c65fd1e2b44ea9e8f8ea0784ac6d0b60624",
    "live_context_source": "deepwiki_briefs/bsc-0x57cf8c65fd1e2b44ea9e8f8ea0784ac6d0b60624.json",
    "live_context_is_current": false
  },
  "hard_gates": {
    "current_live_target_only": true,
    "live_state_supports_preconditions": false,
    "unprivileged_attacker": true,
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
    "Contract holds ~$477K in one or more ERC-20 tokens — confirmed by tvl_usd signal only; specific tokens and balances not verified via direct RPC call",
    "At least one public selector exists that moves tokens to a caller-controlled address — NOT confirmed; no source, no ABI, no decompiled selectors available",
    "No access control (or bypassable access control) guards that selector — NOT confirmed; cannot evaluate without selectors",
    "Deployer identity and funding source are unknown — funding_cluster_id is empty, deployer_address is empty",
    "No transaction history exists to confirm or deny prior interaction patterns — volume24h_usd is 0, no internal transactions listed"
  ],
  "attacker_path": {
    "actor": "unprivileged external EOA",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown ERC-20 token(s) totaling ~$477,006 USD",
    "attacker_gain": "unconfirmed — no selector or code path identified",
    "victim_or_protocol_loss": "unconfirmed — funding source (user deposits vs. self-funded honeypot vs. single large transfer) not determined",
    "why_gain_exceeds_entitlement": "cannot be evaluated without source, selectors, or entitlement logic"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Candidate entered the proof gate with a prior triage verdict of NEEDS_LIVE_CONTEXT. Five of the twelve hard gates fail: live_state_supports_preconditions, attacker_controls_trigger, exact_code_path_or_selector_exists, concrete_fund_or_reward_gain, and gain_is_beyond_entitlement. The root cause is a single missing prerequisite: no bytecode decompilation or selector extraction has been performed. Without at least one confirmed public selector that moves tokens, no call sequence can be constructed, no fork test can be written, and no entitlement comparison can be made. The $477K balance signal is real and the candidate is not rejected on merit — it is rejected because the mandatory live-context collection step (bytecode/selector extraction, deployer trace, token balance breakdown, transaction history, proxy slot check, funding source trace) was skipped before proof-gate submission. Correct routing: return to needs_live_context, execute the six live-context commands from the triage output, then re-submit to triage. If triage then routes to needs_local_proof or deepwiki_candidates, re-enter the proof gate with the collected context attached."
}
```

**Gate outcome summary:**

Five hard gates fail, all traceable to one root cause: no selectors were recovered before this candidate was submitted to the proof gate.

| Hard gate | Result | Reason |
|---|---|---|
| `exact_code_path_or_selector_exists` | FAIL | No verified source, no ABI, no decompiled selectors |
| `attacker_controls_trigger` | FAIL | Cannot identify a callable entrypoint |
| `live_state_supports_preconditions` | FAIL | Token identity, deployer, and tx history all unknown |
| `concrete_fund_or_reward_gain` | FAIL | No confirmed path from balance to attacker wallet |
| `gain_is_beyond_entitlement` | FAIL | No entitlement logic visible without source |

The candidate is not rejected on merit. The $477K balance spike on a fresh unverified zero-volume BSC contract is a legitimate signal. The correct next step is to execute the six live-context commands from the triage output — starting with bytecode decompilation and 4-byte selector extraction — then re-enter triage before re-submitting to the proof gate. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-79)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "gate_question": (
        "Does this exact current protocol, with current live state, allow an "
        "unprivileged attacker to extract funds or rewards beyond entitlement?"
    ),
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "active_target": {
        "chain": "",
        "address": "",
        "live_context_source": "",
        "live_context_is_current": False,
    },
    "hard_gates": {
        "current_live_target_only": False,
        "live_state_supports_preconditions": False,
        "unprivileged_attacker": False,
        "attacker_controls_trigger": False,
        "exact_code_path_or_selector_exists": False,
        "concrete_fund_or_reward_gain": False,
        "gain_is_beyond_entitlement": False,
        "not_dos_grief_or_liveness_only": False,
        "not_admin_governance_or_key_compromise": False,
        "not_external_dependency_only": False,
        "not_expected_behavior": False,
        "not_known_duplicate": False,
    },
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

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L203-234)
```markdown
### Stage 6 - DeepWiki Proof Gate

Reuse MKSIIQO's exact gate:

```text
Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?
```

Input folders:

- `needs_local_proof/*.json`
- `deepwiki_candidates/*.json`

Output contract:

```text
proof-gate-v1
```

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