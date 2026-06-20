<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_0e4489b7-0717-4815-b778-d2355fe725aa?mode=deep -->

The proof gate schema only permits three verdicts: `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. `NEEDS_LIVE_CONTEXT` is a triage-stage verdict and is not valid here. [1](#0-0) 

Every hard gate that requires confirmed live state or a known code path is `false`. No source, ABI, selector, deployer, or funding path exists in the repository or the provided brief. The gate question cannot be answered affirmatively, so the correct proof-gate verdict is `REJECT`. [2](#0-1) 

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0xd21bc2291c1aef340f5265e257b18aa5dafed759",
    "live_context_source": "none — no live context file provided",
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
    "not_dos_grief_or_liveness_only": false,
    "not_admin_governance_or_key_compromise": false,
    "not_external_dependency_only": false,
    "not_expected_behavior": false,
    "not_known_duplicate": false
  },
  "live_preconditions": [],
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
  "rejection_reason": "All hard gates are false. verified_source is null, deployer_address is empty, funding_cluster_id is empty, and no ABI or selector data exists in the repository or the provided brief. exact_code_path_or_selector_exists cannot be satisfied without bytecode decompilation. live_state_supports_preconditions cannot be satisfied without confirmed token balances and a known entrypoint. The gate question requires proof against live state or a reproducible fork state; neither is available. This candidate must complete the NEEDS_LIVE_CONTEXT triage actions (bytecode decompilation, balance confirmation, deployer resolution, proxy check, transaction history review) before it can re-enter the proof gate."
}
```

**Why `REJECT` and not `NEEDS_LOCAL_PROOF`:** `NEEDS_LOCAL_PROOF` requires at least one confirmed selector or code path and confirmed live preconditions so that a fork test can be written. [3](#0-2)  None of those exist here. Promoting to `NEEDS_LOCAL_PROOF` without a known entrypoint would produce an unwritable test. The candidate must resolve the five live-context items from the triage output first, then re-enter this gate.

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** HUNT_PLAN.md (L76-84)
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