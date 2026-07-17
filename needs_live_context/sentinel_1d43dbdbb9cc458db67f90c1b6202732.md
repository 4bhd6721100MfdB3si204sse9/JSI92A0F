<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_ed8ccbd2-887e-4548-bea7-a0332ffe0578?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x303d72b77efe73e07aacb9dbe58e794c3df48625",
    "name": "0x303d72b77efe73e07aacb9dbe58e794c3df48625",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 98
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with ~$8.07M token balance and an immediate balance spike. No deployer, no funding cluster, no verified source in the pipeline state. The contradiction between verified_source:true and the unknown_verification_status tag means source availability is unconfirmed. No selectors, ABI, proxy state, or token identity are known. Value at risk is material but no exploit path can be hypothesized without source or selector data.",
  "live_context_required": [
    {
      "name": "source_code_or_bytecode",
      "reason": "verified_source:true is contradicted by the unknown_verification_status tag. Actual Etherscan source or raw bytecode is required to identify value-moving selectors and access control patterns.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0x303d72b77efe73e07aacb9dbe58e794c3df48625&apikey=<KEY>'"
    },
    {
      "name": "proxy_resolution",
      "reason": "Fresh funded contracts are frequently minimal proxies (EIP-1967, EIP-897, EIP-1167). If a proxy, the implementation address controls all logic and must be resolved before any selector analysis.",
      "command_or_source": "cast storage 0x303d72b77efe73e07aacb9dbe58e794c3df48625 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url <ETH_RPC>"
    },
    {
      "name": "token_balances_and_identity",
      "reason": "The brief records ~$8.07M TVL as token balance but does not identify which token(s) are held. Token identity determines whether the balance is a stablecoin, LP token, governance token, or reward token, which directly affects exploit surface classification.",
      "command_or_source": "cast call 0x303d72b77efe73e07aacb9dbe58e794c3df48625 'balanceOf(address)' <addr> --rpc-url <ETH_RPC>; check Etherscan token holdings tab"
    },
    {
      "name": "deployer_address_and_funding_trace",
      "reason": "deployer_address is empty in the brief. Deployer identity and the funding transaction are needed to determine whether this is a redeployed known-vulnerable contract, a migrator, or a fresh protocol.",
      "command_or_source": "cast tx $(cast receipt $(cast creation-tx 0x303d72b77efe73e07aacb9dbe58e794c3df48625 --rpc-url <ETH_RPC>) --rpc-url <ETH_RPC>) --rpc-url <ETH_RPC>"
    },
    {
      "name": "public_selector_enumeration",
      "reason": "No function selectors are known. Without selectors, no value-moving path (withdraw, redeem, claim, sweep, migrate) can be identified or tested.",
      "command_or_source": "python3 -c \"import requests; r=requests.get('https://api.etherscan.io/api?module=contract&action=getabi&address=0x303d72b77efe73e07aacb9dbe58e794c3df48625&apikey=<KEY>'); print(r.json())\""
    },
    {
      "name": "recent_transaction_history",
      "reason": "The balance_spike and immediate_balance_spike tags indicate a sudden inflow. Transaction history reveals whether funds arrived via a single EOA, a bridge, a migrator, or a protocol deposit — and whether any withdrawals have already occurred.",
      "command_or_source": "curl 'https://api.etherscan.io/api?module=account&action=txlist&address=0x303d72b77efe73e07aacb9dbe58e794c3df48625&sort=asc&apikey=<KEY>'"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or sweep (no access control on value-moving function)",
    "missing access control on claim or redeem",
    "phantom accounting (shares or rewards created without matching assets)",
    "proxy or implementation mismatch exposing live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or source available",
      "evidence": "verified_source:true flag is contradicted by unknown_verification_status tag; no source file exists in deepwiki_briefs for this address",
      "why_it_matters": "Without confirmed selectors, no value-moving path can be identified or ruled out"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Source code or bytecode must be obtained to confirm public value-moving selectors exist",
      "If proxy: implementation address must be resolved",
      "Token identity and withdrawal/claim mechanics must be confirmed"
    ],
    "call_sequence": [
      "UNKNOWN — blocked on selector and source availability"
    ],
    "expected_gain": "UNKNOWN — up to ~$8.07M if an unguarded withdrawal or claim path exists"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Resolve source or bytecode for 0x303d72b77efe73e07aacb9dbe58e794c3df48625",
      "Resolve proxy implementation if applicable",
      "Identify token(s) held and their addresses",
      "Enumerate all external/public selectors",
      "Fork Ethereum mainnet at current block"
    ],
    "transaction_sequence": [
      "BLOCKED — cannot construct until selectors and access control logic are known"
    ],
    "expected_assert