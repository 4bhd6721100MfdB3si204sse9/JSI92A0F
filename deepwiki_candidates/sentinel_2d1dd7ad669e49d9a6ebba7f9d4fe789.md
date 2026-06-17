<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_f597aa9e-315c-4935-ac7e-c2ac9deef30b?mode=deep -->
<!-- deepwiki_verdict: high_confidence_candidate -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0xf0750c373ebbb3baeef7e03d8300caad1983d67c",
    "name": "0xf0750c373ebbb3baeef7e03d8300caad1983d67c",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 103
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$1.17M in bluechip tokens with an immediate balance spike and no verified source. The combination of hidden_high_value_contract, unknown_verification_status, and balance_spike on a fresh deployment is a high-signal pattern for either a honeypot, a custody contract with missing access control, or a redeployed vulnerable vault. No selectors, ABI, deployer address, or transaction history are available in the brief, making exploit hypothesis formation impossible without live recon.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "verified_source is null and unknown_verification_status is set. Without selectors or decompiled bytecode we cannot identify any value-moving functions (withdraw, claim, sweep, redeem, migrate) or determine whether access control exists.",
      "command_or_source": "cast code 0xf0750c373ebbb3baeef7e03d8300caad1983d67c --rpc-url $BSC_RPC | python3 -c 'import sys,evmdasm; evmdasm.disassemble(sys.stdin.read())' OR use heimdall / panoramix to extract 4-byte selectors and reconstruct pseudo-ABI"
    },
    {
      "name": "proxy_implementation_check",
      "reason": "Fresh contracts with large balances are frequently transparent or UUPS proxies. If an implementation slot is set, the real logic lives elsewhere and may have been recently swapped.",
      "command_or_source": "cast storage 0xf0750c373ebbb3baeef7e03d8300caad1983d67c 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC  # EIP-1967 impl slot"
    },
    {
      "name": "deployer_address_and_funding_cluster",
      "reason": "deployer_address and funding_cluster_id are both empty. Tracing the deployer reveals whether this is a known-bad actor, a closed-project redeploy, or a bot-controlled custody address.",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $BSC_RPC) | grep contractAddress) --rpc-url $BSC_RPC  OR  query BSCScan internal-tx API for contract creation tx to extract deployer"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags indicate bluechip_token_balance and known_asset_balance but do not specify which tokens or amounts. Knowing the exact assets (USDT, USDC, WBNB, CAKE, etc.) determines whether the balance is withdrawable via a public transfer path or locked behind logic.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0xf0750c373ebbb3baeef7e03d8300caad1983d67c&sort=asc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "inbound_and_outbound_transaction_history",
      "reason": "immediate_balance_spike tag suggests funds arrived in a short window. Knowing the funding source (EOA, another contract, bridge) and whether any outbound calls have occurred reveals whether this is a live custody contract or a draining-in-progress honeypot.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xf0750c373ebbb3baeef7e03d8300caad1983d67c&sort=asc&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "owner_or_admin_slot",
      "reason": "If the contract exposes an owner() or admin() selector, knowing whether it is set to a known EOA, a multisig, or address(0) determines whether missing-access-control paths are reachable by an unprivileged caller.",
      "command_or_source": "cast call 0xf0750c373ebbb3baeef7e03d8300caad1983d67c 'owner()(address)' --rpc-url $BSC_RPC 2>/dev/null || cast storage 0xf0750c373ebbb3baeef7e03d8300caad1983d67c 0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing_access_control_on_sweep_or_withdraw",
    "uninitialized_proxy_or_implementation_takeover",
    "phantom_accounting_fresh_vault_no_verified_source"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or verified source available",
      "evidence": "verified_source: null; unknown_verification_status tag present; no selectors provided in brief",
      "why_it_matters": "Cannot confirm or deny the existence of any value-moving public function without bytecode decompilation. All exploit families remain hypothetical until selectors are extracted."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$1.17M in bluechip tokens (confirmed by TVL signal)",
      "At least one public selector exists that moves tokens out of the contract",
      "That selector lacks caller validation or uses a broken access-control pattern"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector extraction before a concrete sequence can be formed"
    ],
    "expected_gain": "Up to ~$1,172,994 in bluechip token balance if a public sweep/withdraw/claim selector with no access control exists; amount depends on which tokens are held and whether the full balance is reachable in one call"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC mainnet at current block",
      "Confirm contract balance via token transfer events",
      "Decompile bytecode to extract callable selectors",
      "Identify any withdraw/claim/sweep/transfer selector with no msg.sender check"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot populate until live_context_required items above are resolved"
    ],
    "expected_assertions": [
      "attacker token balance increases by > 0 after call",
      "contract token balance decreases by matching amount",
      "no privileged role was required for the call"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** The contract scores high on signal (large fresh balance, bluechip tokens, hidden/unverified, immediate spike) but every exploit-hypothesis field is blocked by the same root gap: `verified_source: null` with no deployer, no selectors, and no transaction history in the brief. The hard rules require a concrete code/selector path before `NEEDS_LOCAL_PROOF` or `HIGH_CONFIDENCE_CANDIDATE` can be issued. The six `live_context_required` items above are the minimum recon needed to unblock the next stage. [1](#0-0) [2](#0-1)

### Citations

**File:** HUNT_PLAN.md (L75-85)
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