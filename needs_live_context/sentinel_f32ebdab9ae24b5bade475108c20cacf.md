<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_88b33d2f-affd-4a48-a54c-ac52c28df7aa?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0x28e2ea090877bf75740558f6bfb36a5ffee9e9df` has no entry in any run file, deepwiki brief, or state file in this repository. The brief itself confirms `verified_source: null`, no deployer, no selectors, no proxy state, and no transaction patterns — only raw balance tags. Applying the hard rules:

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "name": "0x28e2ea090877bf75740558f6bfb36a5ffee9e9df",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 45
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract holding ~$9.9M in native and token value with no verified source, no known deployer, and no selector inventory. The combination of fresh_contract_large_balance, stablecoin_balance, and unknown_protocol on a high-weight chain (BSC:10) makes this a plausible custody or escrow surface. Without source or selectors, no exploit family can be confirmed, but the value density and opacity are consistent with unverified funded contracts that carry missing-access-control or unauthorized-withdrawal risk.",
  "live_context_required": [
    {
      "name": "verified_source_or_bytecode",
      "reason": "verified_source is null; no function signatures, access control, or logic are known. Bytecode decompilation is the minimum needed to identify value-moving selectors.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&apikey=<KEY>' | jq .result[0].SourceCode"
    },
    {
      "name": "selector_inventory_from_txlist",
      "reason": "No selectors are present in the brief. Transaction calldata methodIds are needed to identify which public functions have been called and whether any are value-moving (withdraw, claim, redeem, sweep, transfer).",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=txlist&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&sort=desc&apikey=<KEY>' | jq '[.result[].methodId] | unique'"
    },
    {
      "name": "proxy_implementation_slot",
      "reason": "Unknown whether this is a proxy. If EIP-1967 or EIP-1822 slots are populated, the implementation contract may carry the actual logic and access control (or lack thereof).",
      "command_or_source": "cast storage 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url <BSC_RPC>"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags indicate stablecoin_balance and known_asset_balance but no token addresses or amounts are enumerated. Knowing which tokens and amounts are held is required to assess extractability.",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=account&action=tokentx&address=0x28e2ea090877bf75740558f6bfb36a5ffee9e9df&sort=desc&apikey=<KEY>' | jq '[.result[] | {token: .tokenSymbol, contract: .contractAddress}] | unique'"
    },
    {
      "name": "deployer_and_funder_cluster",
      "reason": "deployer_address and funding_cluster_id are both empty. Deployer identity and funding source are needed to check for closed-project redeploy patterns and to assess whether the contract is a legitimate custody address or a honeypot/rug surface.",
      "command_or_source": "cast tx $(cast receipt $(cast call --rpc-url <BSC_RPC> -- eth_getTransactionByBlockNumberAndIndex ...) ...) --rpc-url <BSC_RPC>; alternatively check BscScan contract creation tx"
    },
    {
      "name": "admin_owner_role",
      "reason": "No owner or admin is known. If an EOA owns a privileged sweep or rescue function, the risk profile changes. If there is no owner check, unauthorized extraction may be possible.",
      "command_or_source": "cast call 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df 'owner()(address)' --rpc-url <BSC_RPC>"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal, redeem, unstake, claim, liquidate, release, sweep, or migrate",
    "proxy, implementation, or storage mismatch that exposes live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no selectors in brief",
      "evidence": "verified_source is null; no methodIds recovered from transactions; no ABI available",
      "why_it_matters": "Without at least one confirmed value-moving selector, no exploit path can be constructed. This is the primary blocker for advancing to NEEDS_LOCAL_PROOF."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$9.9M in native BNB and/or stablecoins (confirmed by balance tags)",
      "At least one public selector exists that moves value without caller validation (unconfirmed — requires source/bytecode)",
      "No timelock or multisig guards the value-moving path (unconfirmed)"
    ],
    "call_sequence": [
      "1. Identify value-moving selector via bytecode decompilation or txlist methodIds",
      "2. Call selector directly as an unprivileged EOA with attacker-controlled recipient",
      "3. Observe token or native balance transfer to attacker address"
    ],
    "expected_gain": "Unknown until selectors and access control are confirmed. Upper bound is ~$9.9M if a public sweep or withdraw function exists with no caller check."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block: anvil --fork-url <BSC_RPC> --fork-block-number latest",
      "Confirm contract balance: cast balance 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df --rpc-url <FORK_RPC>",
      "Decompile bytecode or load verified ABI once source is retrieved",
      "Identify candidate value-moving selectors"
    ],
    "transaction_sequence": [
      "vm.prank(attacker) — call identified value-moving selector with attacker as recipient",
      "Assert attacker token/native balance increased",
      "Assert contract balance decreased by matching amount"
    ],
    "expected_assertions": [
      "attacker.balance > 0 after call",
      "contract.balance == 0 or reduced by attacker gain",
      "No revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale:** The $9.9M balance on a fresh, unverified, unknown-protocol BSC contract clears the value threshold and chain-weight filters, making it worth pursuing. However, the brief contains zero source, zero selectors, zero deployer data, and zero transaction patterns. Every exploit family hypothesis is blocked by the same gap: no confirmed public value-moving path exists yet. The correct gate is `NEEDS_LIVE_CONTEXT` — retrieve bytecode/source and selector inventory first, then re-triage.