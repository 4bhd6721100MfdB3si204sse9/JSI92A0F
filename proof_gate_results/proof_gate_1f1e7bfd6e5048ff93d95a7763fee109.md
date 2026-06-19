<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_582524e4-53fe-4a6b-9c93-e302af404144?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x3d2bb7e9df6b49b82ec75214aea8feddab78fc5f",
    "live_context_source": "none — address absent from all repository artifacts; candidate brief only",
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
      "precondition": "At least one value-moving external selector is confirmed to exist in the contract bytecode",
      "status": "unmet — verified_source is null, no ABI, no selector list in any repository artifact or brief field",
      "blocking": true
    },
    {
      "precondition": "Confirmed selector is reachable by an unprivileged caller (no owner/role guard, or guard is bypassable)",
      "status": "unmet — no access control analysis possible without selectors",
      "blocking": true
    },
    {
      "precondition": "Token held is a standard transferable ERC-20 (not locked, rebasing, or fee-on-transfer in a way that prevents extraction)",
      "status": "unmet — token identity unknown; TVL=$924,936 with zero volume and zero liquidity",
      "blocking": true
    },
    {
      "precondition": "Proxy implementation (if any) is identified and its logic is available for analysis",
      "status": "unmet — EIP-1967 and beacon slots not read; fresh unverified contract with large balance is a known proxy pattern",
      "blocking": true
    }
  ],
  "attacker_path": {
    "actor": "unprivileged external EOA",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown token(s) — ~$924,936 TVL, zero DEX volume, zero liquidity",
    "attacker_gain": "unquantifiable — no selector, no transfer path confirmed",
    "victim_or_protocol_loss": "unquantifiable",
    "why_gain_exceeds_entitlement": "cannot be determined — no source, no ABI, no call path"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Five hard gates fail simultaneously. (1) exact_code_path_or_selector_exists=false: the contract has no verified source and no ABI; no value-moving selector has been identified in any repository artifact or brief field — this is the single hardest blocker per HUNT_PLAN.md L76-84. (2) live_state_supports_preconditions=false: no live RPC or explorer data was provided; the candidate brief explicitly carries verdict NEEDS_LIVE_CONTEXT and lists six unresolved enrichment steps. (3) unprivileged_attacker=false: without a confirmed selector and access-control read, it is impossible to assert that any function is reachable by an unprivileged caller. (4) attacker_controls_trigger=false: no call sequence can be constructed. (5) concrete_fund_or_reward_gain=false and gain_is_beyond_entitlement=false: no extraction path exists to quantify. The TVL signal (~$925K, balance_spike tags) is real and the pattern (fresh, unverified, zero-volume, large balance) is consistent with high-value extraction surfaces, but signal alone does not satisfy the proof gate. The candidate must complete live enrichment (bytecode/selector extraction, proxy check, deployer trace, token identification, access-control slot reads) before re-entering this gate."
}
```

**Gate outcome: REJECT — insufficient live context to pass any exploit-path hard gate.**

The address `0x3d2bb7e9df6b49b82ec75214aea8feddab78fc5f` appears nowhere in the repository. [1](#0-0)  The proof-gate schema does not carry a `NEEDS_LIVE_CONTEXT` holding state — that verdict belongs to the upstream triage schema only. [2](#0-1)  At the proof gate, a candidate that cannot satisfy `exact_code_path_or_selector_exists` must be rejected and returned to the live-enrichment queue. [3](#0-2)  The hard stop in `HUNT_PLAN.md` requires a reproducible path and gain beyond entitlement — neither can be established without at least one confirmed selector. [4](#0-3)

### Citations

**File:** sentinel_deepwiki_schema.py (L7-9)
```python
TRIAGE_CONTRACT: dict[str, Any] = {
    "schema_version": "sentinel-triage-v1",
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

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