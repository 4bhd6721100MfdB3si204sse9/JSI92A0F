<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_0192bf91-fdbc-4deb-90e0-4a90a528f09f?mode=deep -->

Based on the candidate brief, the proof gate schema, and the hard gate rules defined in the repository, here is the proof gate evaluation:

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "none",
  "active_target": {
    "chain": "bsc",
    "address": "0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735",
    "live_context_source": "deepwiki_briefs/015-bsc-0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735.json",
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
      "name": "liquid_asset_balance_confirmed",
      "status": "NOT_MET",
      "reason": "Reported ~$61B TVL with fdv_usd=0, liquidity_usd=0, and volume24h_usd=0 is the canonical signature of a self-issued or illiquid token. No real liquid asset (WBNB, USDT, BUSD, CAKE) has been confirmed in the contract. Without confirmed liquid value, concrete_fund_or_reward_gain cannot be true.",
      "required_command": "cast call 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 'balanceOf(address)(uint256)' <address> --rpc-url $BSC_RPC; check bscscan.com token holdings tab"
    },
    {
      "name": "public_value_moving_selector_confirmed",
      "status": "NOT_MET",
      "reason": "No verified source, no ABI, no observed transaction input data. Zero selectors are known. exact_code_path_or_selector_exists cannot be true without bytecode decompilation.",
      "required_command": "heimdall-rs decompile 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 --rpc-url $BSC_RPC"
    },
    {
      "name": "access_control_absent_on_value_path",
      "status": "NOT_MET",
      "reason": "No selector surface means no access control analysis is possible. unprivileged_attacker and attacker_controls_trigger both remain false.",
      "required_command": "cast call 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 'owner()(address)' --rpc-url $BSC_RPC"
    },
    {
      "name": "proxy_implementation_resolved",
      "status": "NOT_MET",
      "reason": "EIP-1967 and EIP-897 proxy slots have not been checked. If a proxy, the real selector surface is on the implementation, not this address.",
      "required_command": "cast storage 0x588d7cf062f4edd7c7c7f2d66fd770e03b1ea735 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
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
    "asset_or_reward": "unknown — no liquid asset confirmed",
    "attacker_gain": "unknown — no selector confirmed",
    "victim_or_protocol_loss": "unknown",
    "why_gain_exceeds_entitlement": "cannot be evaluated without a confirmed selector and confirmed liquid balance"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": ""
  },
  "rejection_reason": "Five hard gates fail simultaneously: live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, and concrete_fund_or_reward_gain are all false. The ~$61B TVL figure is almost certainly phantom: fdv_usd, liquidity_usd, and volume24h_usd are all exactly zero, which is the canonical signature of a self-issued or illiquid token inflating the reported balance. No verified source, no ABI, no observed selectors, and no deployer identity are available. No live context was provided to this gate. Per the hard rules in deepwiki_prompts.py (L40), NEEDS_LOCAL_PROOF requires enough source, selector, balance, or transaction evidence — none of those are present. The candidate must return to the NEEDS_LIVE_CONTEXT route: confirm liquid asset identity and real USD value, decompile bytecode to recover selectors, resolve proxy/implementation, and check owner/admin state before re-entering the proof gate."
}
```

**Rationale summary:**

The proof gate has three possible verdicts: `REJECT`, `NEEDS_LOCAL_PROOF`, or `HIGH_CONFIDENCE_CANDIDATE`. [1](#0-0)  `NEEDS_LOCAL_PROOF` is not available here because the gate requires "enough source, selector, balance, or transaction evidence" — none of which exist. [2](#0-1) 

The five simultaneously-failing hard gates are the decisive blockers:

1. **`live_state_supports_preconditions = false`** — no live context was provided to this gate at all.
2. **`exact_code_path_or_selector_exists = false`** — no verified source, no ABI, no bytecode analysis, no observed transaction input data.
3. **`concrete_fund_or_reward_gain = false`** — the ~$61B TVL with `fdv_usd=0`, `liquidity_usd=0`, `volume24h_usd=0` is the canonical phantom-balance signature. [3](#0-2) 
4. **`unprivileged_attacker = false`** — no selector surface means privilege model is entirely unknown.
5. **`attacker_controls_trigger = false`** — no callable entrypoint has been identified.

The `HUNT_PLAN.md` hard stop rule requires a reproducible path and extraction of user funds before any promotion. [4](#0-3)  None of those conditions are met. The correct next action remains `recon_bravo_then_corecritical` — gather live context first, then re-enter the proof gate. [5](#0-4)

### Citations

**File:** sentinel_deepwiki_schema.py (L54-54)
```python
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** deepwiki_prompts.py (L39-41)
```python
- Use NEEDS_LIVE_CONTEXT when the candidate is interesting but live balances, proxy/admin state, selectors, claimability, or source details are missing.
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
```

**File:** run_build_deepwiki_briefs.py (L56-56)
```python
    value = max(float(row.get("liquidity_usd", 0) or 0), float(row.get("tvl_usd", 0) or 0))
```

**File:** HUNT_PLAN.md (L110-116)
```markdown
Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

```

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L370-372)
```markdown
recon_bravo_then_corecritical
-> normal protocol recon

```