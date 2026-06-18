<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_937b02be-4e39-4393-9cc6-33ef9f00273c?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "bsc",
    "address": "0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4",
    "live_context_source": "none — no live context file provided; candidate brief only",
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
      "name": "bytecode_and_selector_recovery",
      "status": "MISSING",
      "reason": "No verified source exists and no decompiled output was provided. Without a selector list, no value-moving entrypoint can be identified. This is the primary hard-gate blocker for exact_code_path_or_selector_exists.",
      "command": "cast code 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 --rpc-url $BSC_RPC | heimdall decompile --stdin"
    },
    {
      "name": "proxy_implementation_check",
      "status": "MISSING",
      "reason": "EIP-1967 and EIP-897 storage slots have not been read. If a live implementation exists behind a proxy shell, the effective ABI may differ entirely from the proxy bytecode. live_state_supports_preconditions cannot be set true until this is resolved.",
      "command": "cast storage 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "status": "MISSING",
      "reason": "The $403K TVL figure is unresolved into specific tokens and amounts. concrete_fund_or_reward_gain requires knowing which assets are held and whether they are withdrawable principal or locked collateral.",
      "command": "BSCScan token holdings tab for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4"
    },
    {
      "name": "deployer_and_funding_trace",
      "status": "MISSING",
      "reason": "deployer_address and funding_cluster_id are both empty. Without deployer identity, it is impossible to assess whether this is a redeploy of a known-vulnerable pattern or a novel contract, blocking not_expected_behavior and not_known_duplicate confidence.",
      "command": "BSCScan internal transactions for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4 — identify creation tx, trace deployer wallet"
    },
    {
      "name": "transaction_history_and_caller_pattern",
      "status": "MISSING",
      "reason": "Zero volume24h and no tx history means it is unknown whether any public entrypoints have been called. attacker_controls_trigger requires at least one confirmed reachable selector with no access-control revert.",
      "command": "BSCScan transactions tab for 0x47a90a2d92a8367a91efa1906bfc8c1e05bf10c4"
    }
  ],
  "attacker_path": {
    "actor": "UNKNOWN — selector enumeration required",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "UNKNOWN — token identity unresolved; $403K TVL attributed to bluechip_token_balance and known_asset_balance tags only",
    "attacker_gain": "UNKNOWN — no value-moving selector identified",
    "victim_or_protocol_loss": "UNKNOWN",
    "why_gain_exceeds_entitlement": "UNKNOWN — no entitlement logic visible without source or decompiled output"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "BLOCKED — cannot name a test file until at least one value-moving selector is recovered and confirmed reachable by an unprivileged caller",
    "setup": [
      "BSC mainnet fork at current block",
      "Bytecode decompilation output identifying at least one value-moving selector",
      "Proxy implementation address resolved (EIP-1967 slot read)",
      "Token balance confirmation via balanceOf calls for all held assets"
    ],
    "transaction_sequence": [
      "BLOCKED — construct only after selector recovery and access-control analysis are complete"
    ],
    "expected_assertions": [
      "attacker token balance increases by > 0 after call",
      "contract token balance decreases by matching amount",
      "no revert due to owner check, whitelist, or merkle proof"
    ],
    "reject_if_assertion_fails": "If all recovered selectors revert for an unprivileged caller, or if no value-moving selector exists, reject candidate permanently."
  },
  "rejection_reason": "PROOF GATE BLOCKED — LIVE CONTEXT NOT PROVIDED. The triage verdict was NEEDS_LIVE_CONTEXT and no live context file was supplied to this gate pass. Five hard-gate fields fail simultaneously: live_state_supports_preconditions, unprivileged_attacker, attacker_controls_trigger, exact_code_path_or_selector_exists, and concrete_fund_or_reward_gain. The root cause is a single upstream blocker: no bytecode decompilation, no selector list, no proxy slot read, no token balance breakdown, and no transaction history. The $403K TVL and balance_spike signal are real and the candidate is not permanently rejected — it must be re-submitted to the proof gate after all five live_preconditions above are resolved. Do not promote to NEEDS_LOCAL_PROOF or HIGH_CONFIDENCE_CANDIDATE until a concrete selector with no access-control gate is confirmed on a BSC fork."
}
```

**Gate outcome summary:**

The proof gate issues `REJECT` on a live-context-blocked basis, not a permanent disqualification. The candidate holds a real signal — `balance_spike` + `hidden_high_value_contract` + `unknown_verification_status` on BSC with ~$403K TVL — but **zero of the five minimum live-context items** from triage were resolved before this gate pass. [1](#0-0) 

The single upstream blocker is the absence of bytecode decompilation output. Every downstream hard gate (`exact_code_path_or_selector_exists`, `attacker_controls_trigger`, `concrete_fund_or_reward_gain`, `gain_is_beyond_entitlement`) is gated on having at least one confirmed value-moving selector reachable by an unprivileged caller. [2](#0-1) 

Re-submit to the proof gate only after completing the five `live_preconditions` listed in the output above, in order: proxy slot read → bytecode decompile → selector access-control check → token balance breakdown → deployer trace. [3](#0-2)

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

**File:** HUNT_PLAN.md (L108-116)
```markdown
## Hard Stop

Do not report a candidate unless the proof shows:

- an unprivileged attacker
- a reproducible path
- extraction of user funds or excess rewards
- gain beyond entitlement

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