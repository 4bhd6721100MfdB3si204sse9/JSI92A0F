<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_5c396b3e-6600-4b4f-9b6d-48855b31bdf9?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x73d8bd54f7cf5fab43fe4ef40a62d390644946db",
    "live_context_source": "none — no live context file provided; candidate arrived at proof gate directly from triage with verdict NEEDS_LIVE_CONTEXT",
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
    "not_dos_grief_or_liveness_only": false,
    "not_admin_governance_or_key_compromise": false,
    "not_external_dependency_only": false,
    "not_expected_behavior": false,
    "not_known_duplicate": true
  },
  "live_preconditions": [
    {
      "name": "verified_source_or_decompiled_selectors",
      "status": "MISSING",
      "reason": "verified_source is null and no bytecode decompilation was provided. No public selectors, value-moving functions, or access control logic can be identified. This is a hard blocker for every downstream gate."
    },
    {
      "name": "token_balance_breakdown",
      "status": "MISSING",
      "reason": "TVL is reported as ~$3.09M but the specific tokens, amounts, and whether any are transferable by a public call are unknown. The balance signal is real but unanchored to any callable path."
    },
    {
      "name": "deployer_address_and_funding_trace",
      "status": "MISSING",
      "reason": "deployer_address is empty. Funding origin, cluster membership, and redeploy pattern cannot be assessed."
    },
    {
      "name": "proxy_and_implementation_slot_reads",
      "status": "MISSING",
      "reason": "EIP-1967 and admin slots have not been read. If the contract is an upgradeable proxy, the implementation may expose selectors not visible from proxy bytecode alone."
    },
    {
      "name": "recent_transaction_history",
      "status": "MISSING",
      "reason": "volume24h_usd is 0.0. No inbound or outbound transaction list has been recovered. Whether any privileged or public caller has already interacted with value-moving selectors is unknown."
    },
    {
      "name": "owner_and_access_control_slots",
      "status": "MISSING",
      "reason": "Storage slots 0, 1, and known Ownable/AccessControl slots have not been read. Whether access control is absent, zeroed, or trivially bypassable cannot be determined."
    }
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token identity and transferability unconfirmed",
    "attacker_gain": "unknown — no callable path identified",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot be evaluated without at least one identified public selector"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "All hard gates that require code-level evidence are false. The candidate entered the proof gate carrying a triage verdict of NEEDS_LIVE_CONTEXT with zero live context resolved: no source, no selectors, no deployer, no transaction history, no proxy slot reads, no owner slot reads. The value signal ($3.09M, balance_spike, hidden_high_value_contract) is real and the candidate is not rejected on merit — it is rejected at this gate because the proof gate cannot evaluate any of the required conditions without the six live_context_required items listed above. Correct routing: return to NEEDS_LIVE_CONTEXT queue, execute all six live_context commands, then re-submit to the proof gate with a populated live context file."
}
```

**Gate outcome explanation:**

The proof gate has only three valid verdicts per `PROOF_GATE_CONTRACT` in `sentinel_deepwiki_schema.py`: `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0) 

`NEEDS_LOCAL_PROOF` requires that `exact_code_path_or_selector_exists` and `live_state_supports_preconditions` are both satisfiable — neither is, because no source, ABI, or decompiled bytecode was provided. [2](#0-1) 

Per the hard stop rule in `HUNT_PLAN.md`, a candidate must not be promoted unless an unprivileged attacker, a reproducible path, and gain beyond entitlement are all demonstrated. None of those three conditions can be evaluated here. [3](#0-2) 

The correct next action is to execute the six `live_context_required` commands from the triage brief (source/bytecode recovery, token balance breakdown, deployer trace, proxy slot reads, transaction history, owner slot reads), then re-submit to the proof gate with a populated live context file. [4](#0-3)

### Citations

**File:** sentinel_deepwiki_schema.py (L52-54)
```python
PROOF_GATE_CONTRACT: dict[str, Any] = {
    "schema_version": "proof-gate-v1",
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** sentinel_deepwiki_schema.py (L66-79)
```python
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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```

**File:** PLAN.md (L149-165)
```markdown
For unverified funded contracts:

1. Identify native/ERC20 balances and recent depositors.
2. Recover function selectors from transaction calldata.
3. Check proxy slots, delegatecall patterns, and implementation addresses.
4. Cluster privileged callers, deployer, and funders.
5. Promote exploitable value-moving functions into proof work.

For redeploy/funding-cluster candidates:

1. Trace funding from the closed project to the new deployment.
2. Compare deployers, owners, treasuries, websites, names, and bytecode.
3. Identify where user funds are currently deposited.
4. Promote the live funded surface into recon and proof.

Output target:

```