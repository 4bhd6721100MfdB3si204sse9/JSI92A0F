<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_c39ab1cc-0ec8-4d11-941d-83716025a2f6?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0x0000000aa232009084bd71a5797d089aa4edfad4",
    "live_context_source": "deepwiki_briefs/ethereum-0x0000000aa232009084bd71a5797d089aa4edfad4.json",
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
    "At least one public or external selector that moves tokens or ETH to a caller-controlled address must exist in the bytecode — NOT YET CONFIRMED: no ABI, no verified source, no decompiled selectors available",
    "That selector must be callable without an owner check, role gate, or whitelist — NOT YET CONFIRMED: access-control slots 0–5 have not been read",
    "Live token balance must remain in the contract at call time — PARTIALLY CONFIRMED: balance_spike tag and tvl_usd=771532 signal value is present, but specific token breakdown and current block balance are unverified",
    "Contract must not be a proxy whose implementation has already been swept or bricked — NOT YET CONFIRMED: EIP-1967 slot 0x360894... has not been read"
  ],
  "attacker_path": {
    "actor": "unprivileged external user",
    "attacker_inputs": [],
    "call_sequence": [],
    "state_before": [],
    "state_after": []
  },
  "extraction_analysis": {
    "asset_or_reward": "unknown — token breakdown not available; tags indicate bluechip_token_balance, tvl_usd=771532",
    "attacker_gain": "unquantifiable — no callable selector confirmed",
    "victim_or_protocol_loss": "unquantifiable — depositor count and custody model unknown",
    "why_gain_exceeds_entitlement": "cannot be stated — no entitlement model is visible without source or selectors"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "foundry_targets/ethereum_0x0000000aa232009084bd71a5797d089aa4edfad4/test/DrainTest.t.sol",
    "setup": [
      "Complete recon_bravo phase first: fetch bytecode via cast code, decompile with heimdall or panoramix, enumerate all 4-byte selectors",
      "Read EIP-1967 proxy slot (0x360894a13ba1a3210667c828492db98dca3e2076) and EIP-897 slot to detect proxy; if proxy, decompile implementation instead",
      "Read storage slots 0–5 for owner/role patterns",
      "Resolve token balances (USDC, WETH, USDT, ETH) via cast call <ERC20> balanceOf(address) at current block",
      "Trace deployer via Etherscan getcontractcreation API; map funding cluster",
      "Pull full tx list via Etherscan txlist API to identify which selectors have been called and by whom",
      "Fork Ethereum mainnet at the block where balance_spike was first observed"
    ],
    "transaction_sequence": [
      "For each decompiled value-moving selector (withdraw, claim, sweep, rescue, transfer, migrate, release): vm.prank(attacker); target.call(abi.encodeWithSelector(selector, ...attacker_address...))",
      "Record token.balanceOf(attacker) and token.balanceOf(target) before and after each call",
      "If proxy: repeat against implementation address directly with delegatecall context"
    ],
    "expected_assertions": [
      "assertGt(token.balanceOf(attacker), 0) — attacker received tokens without prior deposit",
      "assertLt(token.balanceOf(target), balanceBefore) — contract balance reduced",
      "No revert on the call path with unprivileged msg.sender"
    ],
    "reject_if_assertion_fails": "If no selector transfers value to an unprivileged caller without revert, reject permanently. If all value-moving selectors revert or require owner/role, reject. If balance is zero at fork block, reject."
  },
  "rejection_reason": "Proof gate fails on five hard gates: live_state_supports_preconditions=false, unprivileged_attacker=false, attacker_controls_trigger=false, exact_code_path_or_selector_exists=false, concrete_fund_or_reward_gain=false. No ABI, no verified source, no decompiled selectors, no deployer trace, no transaction history, and no proxy-slot data are present in the brief or live context. The balance signal (tvl_usd=771532, balance_spike) is a legitimate priority indicator but is not sufficient to pass the gate without a confirmed callable path. Per HUNT_PLAN.md hard stop: a reproducible path and gain beyond entitlement must be proven before promotion. Re-enter this gate after recon_bravo completes and at least one unguarded value-moving selector is confirmed."
}
```

**Why `REJECT` and not `NEEDS_LOCAL_PROOF`:**

The proof gate schema has no `NEEDS_LIVE_CONTEXT` output slot — that verdict belongs to the triage stage. [1](#0-0)  The gate must choose from `REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE`, and `NEEDS_LOCAL_PROOF` requires that "the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt." [2](#0-1)  None of that evidence exists here.

The `HUNT_PLAN.md` hard stop is explicit: [3](#0-2)  a reproducible path and gain beyond entitlement must be demonstrated before promotion. The five failing hard gates (`exact_code_path_or_selector_exists`, `live_state_supports_preconditions`, `attacker_controls_trigger`, `concrete_fund_or_reward_gain`, `gain_is_beyond_entitlement`) all trace back to the same root cause: no bytecode selectors have been extracted. [4](#0-3) 

The correct re-entry path is: complete `recon_bravo` (bytecode → selectors → proxy check → deployer trace → token balance breakdown → tx history), then re-submit to this gate with that live context populated.

### Citations

**File:** sentinel_deepwiki_schema.py (L54-54)
```python
    "verdict": "REJECT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
```

**File:** deepwiki_prompts.py (L40-41)
```python
- Use NEEDS_LOCAL_PROOF only when the candidate has enough source, selector, balance, or transaction evidence for a local proof attempt.
- Use HIGH_CONFIDENCE_CANDIDATE only when the code/selector path and live value-at-risk line up strongly.
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