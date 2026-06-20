<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_2fff73d9-2354-442a-a7f3-0c0e1be30ff7?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The address `0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8` has no entry anywhere in the repository — no deepwiki brief, no run output, no state file. The brief itself carries `verified_source: null`, no deployer, no selectors, no proxy/admin state, and no transaction patterns. Per the hard rules, this is `NEEDS_LIVE_CONTEXT`.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs/021-bsc-0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8.json",
    "chain": "bsc",
    "address": "0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8",
    "name": "0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Unverified BSC contract holding ~$98.7M in token value with no known protocol identity, no deployer attribution, and no source. The combination of fresh_contract_large_token_balance, hidden_high_value_contract, and unknown_verification_status at this TVL level makes it a priority recon surface for unauthorized withdrawal or sweep paths — but no selector, source, proxy, or transaction evidence exists yet to form a hypothesis.",
  "live_context_required": [
    {
      "name": "contract_source_or_bytecode",
      "reason": "verified_source is null and no ABI or selector list is present; without source or decompiled bytecode there is no basis to identify value-moving functions or access control",
      "command_or_source": "cast etherscan-source --chain bsc 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 || cast disassemble $(cast code --rpc-url $BSC_RPC 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8)"
    },
    {
      "name": "public_selectors",
      "reason": "no selectors are recorded; needed to identify withdraw, redeem, claim, sweep, or migrate entry points callable by an unprivileged address",
      "command_or_source": "cast 4byte-decode on each 4-byte prefix extracted from bytecode, or use heimdall-rs / panoramix decompiler against the deployed bytecode"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "tvl_usd ~$98.7M is attributed to token holdings but no token addresses, symbols, or amounts are listed; needed to confirm real custodied value and identify the asset at risk",
      "command_or_source": "cast call --rpc-url $BSC_RPC 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 'balanceOf(address)' <token> or query BscScan token holdings API for the address"
    },
    {
      "name": "proxy_and_admin_slot_state",
      "reason": "no proxy or implementation data is present; a proxy with a live implementation change or missing admin guard is a direct fund-extraction surface",
      "command_or_source": "cast storage --rpc-url $BSC_RPC 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 0x360894a13ba1a3210667c828492db98dca3e2076 && cast storage ... 0xb53127684a568b3173ae13b9f8a6016f243e3b8a"
    },
    {
      "name": "deployer_address_and_funding_history",
      "reason": "deployer_address is empty; deployer identity and funding source are needed to detect redeploy clusters, closed-project migrations, or exploit-linked wallets",
      "command_or_source": "BscScan contract creation tx: https://bscscan.com/address/0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 -> 'Contract Creator' field"
    },
    {
      "name": "recent_transaction_patterns",
      "reason": "volume24h_usd is 0.0 but the contract holds ~$98.7M; zero volume on a large-balance contract is anomalous — need to confirm whether deposits are recent, whether withdrawals have been attempted, and whether any bot addresses interact repeatedly",
      "command_or_source": "BscScan internal tx and token transfer tabs for 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8, or cast logs --rpc-url $BSC_RPC --address 0xcaaf3c41a40103a23eeaa4bba468af3cf5b0e0d8 --from-block <deploy_block>"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, or sweep",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selectors available",
      "evidence": "verified_source is null; bytecode not yet retrieved; no transaction-level selector data in the brief",
      "why_it_matters": "Without at least one confirmed public selector that moves value, no attacker path hypothesis can be formed and no local proof can be scoped"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "contract source or decompiled selectors must be obtained first",
      "at least one public value-moving function (withdraw, redeem, claim, sweep) must exist without caller restriction",
      "token balance confirmed as real custodied value, not a reflection token or accounting artifact"
    ],
    "call_sequence": [],
    "expected_gain": "unknown — cannot be estimated without selector and source evidence"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "obtain bytecode and decompile or verify source",
      "confirm token holdings and custodied asset addresses",
      "identify at least one public value-moving selector",
      "check proxy slots and admin state"
    ],
    "transaction_sequence": [],
    "expected_assertions": []
  },
  "rejection_reason": ""
}
```

**Rationale for `NEEDS_LIVE_CONTEXT` over `REJECT`:**

The ~$98.7M TVL is real signal. The `hidden_high_value_contract` + `unknown_verification_status` + `fresh_contract_large_token_balance` tag cluster is exactly the pattern the pipeline is designed to catch. However, every field that would support a hypothesis — source, selectors, deployer, proxy state, token breakdown, transaction history — is absent. There is no basis to form an attacker path, and no basis to reject either. The six live-context items above are the minimum needed to route this to `NEEDS_LOCAL_PROOF` or `REJECT` on the next pass.