<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_35e727f0-8997-47dd-9f78-1d74f238b699?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/006-bsc-0x916f992df86795f24de6c268cfb9031fbb1155da.json",
    "chain": "bsc",
    "address": "0x916f992df86795f24de6c268cfb9031fbb1155da",
    "name": "0x916f992df86795f24de6c268cfb9031fbb1155da",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 103
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh unverified BSC contract with ~$1.77M in stablecoin value and an immediate balance spike. No deployer, no source, no selectors, and no transaction history are present in the brief. The combination of hidden_high_value_contract, stablecoin_balance, and unknown_verification_status on a zero-volume fresh contract is consistent with a custody or distribution contract that has not yet been publicly interacted with. If public value-moving selectors exist without access control, an unprivileged caller could drain the stablecoin balance. Cannot form a concrete exploit hypothesis without source or selector evidence.",
  "live_context_required": [
    {
      "name": "contract_source_or_bytecode",
      "reason": "verified_source is null and no ABI or selector list is present. Source code or decompiled bytecode is required to identify public value-moving functions (withdraw, claim, sweep, redeem, transfer, etc.) and any access control guards.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x916f992df86795f24de6c268cfb9031fbb1155da&apikey={api_key}' ; cast code 0x916f992df86795f24de6c268cfb9031fbb1155da --rpc-url $BSC_RPC_URL"
    },
    {
      "name": "transaction_history_and_selectors",
      "reason": "volume24h_usd is 0 and no selectors were recovered. The txlist feed will reveal which method IDs have been called, who called them, and whether any value-moving calls have already occurred. Zero volume on a $1.77M contract is anomalous and may indicate the contract has not yet been publicly discovered.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x916f992df86795f24de6c268cfb9031fbb1155da&sort=asc&apikey={api_key}'"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags confirm stablecoin_balance and known_asset_balance but the brief does not list which tokens or amounts. The token transfer feed and direct balanceOf calls are needed to confirm which stablecoins (USDT, USDC, BUSD, etc.) are held and in what quantities, and to verify the $1.77M figure.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0x916f992df86795f24de6c268cfb9031fbb1155da&apikey={api_key}' ; cast call <token_address> 'balanceOf(address)(uint256)' 0x916f992df86795f24de6c268cfb9031fbb1155da --rpc-url $BSC_RPC_URL"
    },
    {
      "name": "deployer_address_and_funding_path",
      "reason": "deployer_address is empty and funding_cluster_id is empty. The creation transaction is needed to identify the deployer, trace the funding source, and check whether the deployer is linked to a closed project, exploit wallet, or known rug cluster.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x916f992df86795f24de6c268cfb9031fbb1155da&apikey={api_key}'"
    },
    {
      "name": "proxy_implementation_and_admin_slots",
      "reason": "No proxy state is known. If the contract is an EIP-1967 proxy, the implementation address determines the actual code surface. A missing or zero implementation slot rules out proxy complexity; a non-zero slot requires fetching and decompiling the implementation separately.",
      "command_or_source": "cast storage 0x916f992df86795f24de6c268cfb9031fbb1155da 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC_URL ; cast storage 0x916f992df86795f24de6c268cfb9031fbb1155da 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC_URL"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_value_moving_function",
    "unauthorized_withdrawal_or_sweep",
    "phantom_accounting_or_unchecked_claim"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selectors recovered",
      "evidence": "verified_source is null, volume24h_usd is 0.0, and no transaction calldata is present in the brief. No selector list was produced by the enrichment pipeline.",
      "why_it_matters": "Without at least one observed selector or a decompiled function list, no exploit path can be constructed. All three suspected families require confirming that a public entry point exists with insufficient access control."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$1.77M in stablecoins (confirmed by scoring tags)",
      "At least one public selector exists that moves token value (unconfirmed — requires source or bytecode)",
      "The selector lacks an owner/role check or the check is bypassable (unconfirmed)"
    ],
    "call_sequence": [
      "STEP 1 (UNKNOWN): Identify public value-moving selector from decompiled bytecode or source",
      "STEP 2 (UNKNOWN): Determine whether caller is restricted; if not, call directly",
      "STEP 3 (UNKNOWN): Receive stablecoin transfer to attacker address"
    ],
    "expected_gain": "Up to ~$1,770,177 in stablecoins — unconfirmable without selector evidence"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Obtain BSC RPC URL and pin to a recent block where the $1.77M balance is confirmed",
      "Decompile bytecode or obtain verified source to populate ITarget interface",
      "Identify at least one public value-moving selector"
    ],
    "transaction_sequence": [
      "vm.createSelectFork(BSC_RPC_URL)",
      "assertGt(IERC20(stablecoin).balanceOf(TARGET), 0) — confirm live balance",
      "vm.prank(address(0xdead)) — unprivileged caller",
      "TARGET.call(abi.encodeWithSelector(<value_moving_selector>, attacker, amount))",
      "assertGt(IERC20(stablecoin).balanceOf(attacker), 0) — confirm extraction"
    ],
    "expected_assertions": [
      "Attacker stablecoin balance increases after call",
      "Target stablecoin balance decreases by matching amount",
      "No revert from access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:**

The candidate scores `NEEDS_LIVE_CONTEXT` rather than `REJECT` because the value signal is real (~$1.77M stablecoin, confirmed by `known_asset_balance` and `stablecoin_balance` tags) and the `balance_spike` + `immediate_balance_spike` pattern on a zero-volume fresh unverified contract is a genuine anomaly worth investigating.

It cannot advance to `NEEDS_LOCAL_PROOF` because every required input for a proof attempt is missing:

| Required input | Status |
|---|---|
| Source code or ABI | `verified_source: null` |
| Selectors from transactions | `volume24h_usd: 0`, none recovered |
| Deployer identity | `deployer_address: ""` |
| Proxy/implementation state | not checked |
| Token breakdown | tags only, no amounts or addresses |

The five `live_context_required` items above, executed against the BSC explorer and RPC, are the minimum needed to decide whether this advances to `NEEDS_LOCAL_PROOF` or is rejected as a non-exploitable custody contract (e.g., a CEX hot wallet, a bridge escrow with admin-only withdrawal, or a legitimate protocol with proper access control). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L40-47)
```markdown
DeepWiki should never mark a candidate final. It should only classify and produce proof-ready work:

- `REJECT`
- `NEEDS_LIVE_CONTEXT`
- `NEEDS_LOCAL_PROOF`
- `HIGH_CONFIDENCE_CANDIDATE`

Final confirmation remains local: code review, fork/live proof, or a runnable PoC.
```

**File:** sentinel_deepwiki_schema.py (L7-49)
```python
TRIAGE_CONTRACT: dict[str, Any] = {
    "schema_version": "sentinel-triage-v1",
    "verdict": "REJECT | NEEDS_LIVE_CONTEXT | NEEDS_LOCAL_PROOF | HIGH_CONFIDENCE_CANDIDATE",
    "candidate": {
        "source_file": "",
        "chain": "",
        "address": "",
        "name": "",
        "entity_type": "",
        "next_action": "",
        "score": 0,
    },
    "paid_scope_match": "fund_extraction | protocol_value_drain | reward_extraction | unfair_reward_access | none",
    "why_this_target_matters": "",
    "live_context_required": [
        {
            "name": "",
            "reason": "",
            "command_or_source": "",
        }
    ],
    "suspected_exploit_families": [],
    "source_or_selector_basis": [
        {
            "selector_or_function": "",
            "evidence": "",
            "why_it_matters": "",
        }
    ],
    "attacker_path_hypothesis": {
        "actor": "unprivileged external user",
        "preconditions": [],
        "call_sequence": [],
        "expected_gain": "",
    },
    "local_proof_required": {
        "test_type": "fork | unit | invariant | fuzz | manual",
        "setup": [],
        "transaction_sequence": [],
        "expected_assertions": [],
    },
    "rejection_reason": "",
}
```

**File:** config/sentinel.json (L121-145)
```json
  "live_explorers": {
    "bsc": {
      "api_key": "",
      "source_code_url": "https://api.bscscan.com/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}",
      "txlist_url": "https://api.bscscan.com/api?module=account&action=txlist&address={address}&apikey={api_key}",
      "tokentx_url": "https://api.bscscan.com/api?module=account&action=tokentx&address={address}&apikey={api_key}",
      "rpc_url": "",
      "native_price_usd": 1
    },
    "ethereum": {
      "api_key": "",
      "source_code_url": "https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}",
      "txlist_url": "https://api.etherscan.io/api?module=account&action=txlist&address={address}&apikey={api_key}",
      "tokentx_url": "https://api.etherscan.io/api?module=account&action=tokentx&address={address}&apikey={api_key}",
      "rpc_url": "",
      "native_price_usd": 1
    },
    "base": {
      "api_key": "",
      "source_code_url": "https://api.basescan.org/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}",
      "txlist_url": "https://api.basescan.org/api?module=account&action=txlist&address={address}&apikey={api_key}",
      "tokentx_url": "https://api.basescan.org/api?module=account&action=tokentx&address={address}&apikey={api_key}",
      "rpc_url": "",
      "native_price_usd": 1
    }
```

**File:** run_materialize_foundry_target.py (L205-214)
```python
def _proxy(candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "chain": candidate["chain"],
        "target": candidate["address"],
        "eip1967_implementation_slot": "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
        "eip1967_admin_slot": "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103",
        "implementation": _nested_get(payload, ["active_target", "implementation"]) or _nested_get(payload, ["proxy", "implementation"]),
        "admin": _nested_get(payload, ["active_target", "admin"]) or _nested_get(payload, ["proxy", "admin"]),
        "source": "candidate payload if available; otherwise run cast storage against the listed slots",
    }
```