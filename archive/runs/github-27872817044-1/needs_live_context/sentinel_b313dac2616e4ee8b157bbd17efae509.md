<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_c85a8a38-3223-4efe-bf38-a4c55e3d27f4?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/025-bsc-0xabe0e16758e0ec57848a092285ace3b384c58d88.json",
    "chain": "bsc",
    "address": "0xabe0e16758e0ec57848a092285ace3b384c58d88",
    "name": "0xabe0e16758e0ec57848a092285ace3b384c58d88",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$11.4M in token value with no verified source, no known deployer, no known selectors, and no protocol identity. The combination of hidden_high_value_contract + unknown_verification_status + fresh_contract_large_token_balance at this TVL tier is the highest-priority surface for unauthorized withdrawal or sweep paths. No triage is possible without bytecode, selector, or proxy state.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_extraction",
      "reason": "Contract source is unverified (verified_source: null). Bytecode must be pulled and 4-byte selectors extracted to identify any public value-moving functions (withdraw, redeem, claim, sweep, migrate, release).",
      "command_or_source": "cast code 0xabe0e16758e0ec57848a092285ace3b384c58d88 --rpc-url $BSC_RPC | python3 -c 'import sys; b=sys.stdin.read().strip(); [print(b[i:i+8]) for i in range(2,len(b),8) if i+8<=len(b)]' | sort -u  # then resolve via https://www.4byte.directory/"
    },
    {
      "name": "proxy_slot_check",
      "reason": "Unknown whether this is a proxy. If EIP-1967 implementation slot is populated, the real logic lives elsewhere and the implementation address must be fetched and decompiled separately.",
      "command_or_source": "cast storage 0xabe0e16758e0ec57848a092285ace3b384c58d88 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC && cast storage 0xabe0e16758e0ec57848a092285ace3b384c58d88 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "TVL is $11.4M but is entirely token-denominated (liquidity_usd: 0, fdv_usd: 0). The specific token(s) held must be identified to assess whether they are user-deposited principal, reward emissions, or protocol-owned reserves.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokenlist&address=0xabe0e16758e0ec57848a092285ace3b384c58d88&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "deployer_address is empty in the brief. The deployer identity and funding source are required to assess redeploy-cluster risk, closed-project migration, or exploit-linked wallet patterns.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xabe0e16758e0ec57848a092285ace3b384c58d88&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "recent_transaction_selector_patterns",
      "reason": "Transaction history reveals which selectors are actively called, whether withdrawals or claims are occurring, and whether a bot or single address is repeatedly interacting before balance changes.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0xabe0e16758e0ec57848a092285ace3b384c58d88&sort=desc&page=1&offset=50&apikey=$BSCSCAN_KEY'"
    },
    {
      "name": "owner_or_admin_slot",
      "reason": "Common storage slot 0x0 often holds an owner address. If the owner is an EOA or a recently changed address, admin-gated sweep functions become relevant to the access-control check.",
      "command_or_source": "cast storage 0xabe0e16758e0ec57848a092285ace3b384c58d88 0 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no verified source or ABI",
      "evidence": "verified_source is null; no selectors observed in brief; bytecode not yet fetched",
      "why_it_matters": "Without selectors, no exploit family can be confirmed or ruled out. The entire triage is blocked on bytecode extraction."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$11.4M in token value (confirmed by TVL signal)",
      "At least one public selector exists that moves tokens out of the contract",
      "No caller restriction on that selector, or restriction is bypassable"
    ],
    "call_sequence": [
      "UNKNOWN — requires selector extraction and decompilation before a concrete sequence can be formed"
    ],
    "expected_gain": "Unknown — bounded above by ~$11.4M token balance; actual gain depends on selector access control and entitlement logic"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block",
      "Confirm token balances in contract match TVL signal",
      "Identify all public selectors via bytecode decompilation",
      "Determine if any selector moves tokens without caller restriction"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot be specified until selectors and access control are known from live context step"
    ],
    "expected_assertions": [
      "BLOCKED — depends on selector and entitlement logic discovered in live context step"
    ]
  },
  "rejection_reason": ""
}
```

**Verdict rationale:** The $11.4M TVL and `hidden_high_value_contract` + `unknown_verification_status` tag combination clears the interest threshold, but every triage gate is blocked: no source, no selectors, no deployer, no proxy state, no transaction patterns. Per the hard rules, `NEEDS_LIVE_CONTEXT` is the correct route — not `NEEDS_LOCAL_PROOF`, because there is no selector or code path evidence to build a proof sequence from. The six live-context commands above are the minimum required before this candidate can be re-submitted for a proof-gate pass.