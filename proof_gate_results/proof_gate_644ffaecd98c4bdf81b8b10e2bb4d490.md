<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-exact-proof_5ac944d3-3fcb-4e8c-afcb-47eed0e97fa8?mode=deep -->

```json
{
  "schema_version": "proof-gate-v1",
  "verdict": "REJECT",
  "gate_question": "Does this exact current protocol, with current live state, allow an unprivileged attacker to extract funds or rewards beyond entitlement?",
  "paid_scope_match": "fund_extraction",
  "active_target": {
    "chain": "ethereum",
    "address": "0x52aa899454998be5b000ad077a46bbe360f4e497",
    "live_context_source": "none — address absent from all repository state files",
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
  "live_preconditions": [
    {
      "name": "verified_source_or_decompiled_bytecode",
      "satisfied": false,
      "reason": "verified_source is null; address does not appear in any repository file including state/ethereum_chain_scanner.json, runs/, deepwiki_briefs/, or any brief. No bytecode, ABI, or selector list is present."
    },
    {
      "name": "public_selector_enumeration",
      "satisfied": false,
      "reason": "No ABI or function selector list exists in the repository for this address. Without selectors, no value-moving path (withdraw, redeem, sweep, claim, migrate) can be identified or tested."
    },
    {
      "name": "proxy_implementation_check",
      "satisfied": false,
      "reason": "EIP-1967 and OpenZeppelin beacon slots have not been read. If a recent implementation swap occurred, storage layout or access control may be broken — but this cannot be assessed without live RPC data."
    },
    {
      "name": "deployer_address_and_funding_path",
      "satisfied": false,
      "reason": "deployer_address is empty. Cannot determine whether this is a rug-redeploy, bridge escrow, or legitimate protocol without tracing the creation transaction."
    },
    {
      "name": "live_token_balances_and_asset_types",
      "satisfied": false,
      "reason": "TVL of ~$93M is reported via tags only (balance_spike, high_native_balance, stablecoin_balance). Specific token addresses, exact amounts, and current block-level balances are not recorded in any repository state file."
    },
    {
      "name": "access_control_state",
      "satisfied": false,
      "reason": "Common admin/owner slots (0x0–0x5, DEFAULT_ADMIN_ROLE, OWNER_SLOT) have not been read. Cannot determine whether privileged roles are set to address(0) or a burned key."
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
    "asset_or_reward": "unknown — token composition of ~$93M TVL not confirmed in repository state",
    "attacker_gain": "unquantifiable — no selector or code path identified",
    "victim_or_protocol_loss": "unquantifiable — no confirmed drain path",
    "why_gain_exceeds_entitlement": "cannot be established without source, ABI, or selector evidence"
  },
  "local_proof_required": {
    "test_type": "fork",
    "test_file_to_add": "",
    "setup": [
      "Resolve all six live_preconditions above before re-submitting to this gate",
      "cast etherscan-source 0x52aa899454998be5b000ad077a46bbe360f4e497 --chain mainnet OR decompile bytecode with heimdall/panoramix",
      "cast storage 0x52aa899454998be5b000ad077a46bbe360f4e497 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC (EIP-1967 impl slot)",
      "Enumerate all public selectors; identify any withdraw/redeem/sweep/claim/migrate with no caller check",
      "Confirm live ETH and token balances at current block"
    ],
    "transaction_sequence": [],
    "expected_assertions": [],
    "reject_if_assertion_fails": "No value-moving selector with missing access control is found after full bytecode decompilation"
  },
  "rejection_reason": "All positive hard gates fail. The address 0x52aa899454998be5b000ad077a46bbe360f4e497 is entirely absent from the repository — it does not appear in state/ethereum_chain_scanner.json, any run output, any brief, or any source file. verified_source is null, deployer_address is empty, and no ABI or selector list exists anywhere in the codebase. The $93M TVL signal and balance_spike tags are genuine risk indicators, but they satisfy none of the hard gates: there is no exact code path, no confirmed live state, no identified selector, and no quantifiable attacker gain. Per HUNT_PLAN.md hard stop rules, a candidate cannot be promoted unless a reproducible path, an unprivileged attacker trigger, and gain beyond entitlement are all proven. None of the three can be established from repository state alone. Re-submit after resolving all six live_preconditions listed above."
}
```

**Basis for `REJECT` rather than `NEEDS_LOCAL_PROOF`:**

The proof gate schema has no `NEEDS_LIVE_CONTEXT` tier. `NEEDS_LOCAL_PROOF` requires that an exact code path or selector already exists to write a fork test against. Here, `exact_code_path_or_selector_exists` is `false` — there is no source, no ABI, and no decompiled output in the repository. A fork test cannot be written without first completing live recon. The address is confirmed absent from every state file in the repository. [1](#0-0) [2](#0-1)

### Citations

**File:** state/ethereum_chain_scanner.json (L1-10)
```json
{
  "last_scanned_block": 100,
  "seen_contracts": {
    "0x1212121212121212121212121212121212121212": {
      "created_at_ms": null,
      "deployer": "",
      "deployment_tx": "0xtransfer01",
      "discovery_source": "erc20_transfer_log",
      "first_seen_block": 100,
      "last_seen_block": 100,
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