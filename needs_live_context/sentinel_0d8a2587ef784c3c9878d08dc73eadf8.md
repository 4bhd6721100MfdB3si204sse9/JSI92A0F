<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_c27da466-9ee5-4e88-b985-bb9da9b15127?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0x278d858f05b94576c1e6f73285886876ff6ef8d2` does not appear anywhere in the repository — no source, no ABI, no selectors, no transaction traces. The brief's `verified_source: true` flag conflicts with the `unknown_verification_status` tag, suggesting the explorer may have source available but it has not been fetched or analyzed yet. All scoring weight came from balance-spike and freshness signals, not from any structural analysis of the contract itself. Without selectors, source, or deployer context, no exploit family can be confirmed or ruled out.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "deepwiki_briefs (not yet generated for this address)",
    "chain": "bsc",
    "address": "0x278d858f05b94576c1e6f73285886876ff6ef8d2",
    "name": "0x278d858f05b94576c1e6f73285886876ff6ef8d2",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 94
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh BSC contract with ~$766k stablecoin TVL, an immediate balance spike, and no known protocol identity. The combination of hidden_high_value_contract + balance_spike + stablecoin_balance on a fresh unidentified contract is a pattern consistent with a custody or claim contract that may have public value-moving selectors. No source, ABI, deployer, or selector data is available in the current pipeline state, so exploitability cannot be assessed.",
  "live_context_required": [
    {
      "name": "verified_source_code",
      "reason": "brief flags verified_source:true but no source has been fetched or stored; the unknown_verification_status tag contradicts this — must resolve which is correct and retrieve the actual Solidity or bytecode",
      "command_or_source": "curl 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x278d858f05b94576c1e6f73285886876ff6ef8d2&apikey=<KEY>'"
    },
    {
      "name": "public_selectors",
      "reason": "without ABI or bytecode disassembly there is no way to identify withdraw/redeem/claim/sweep entry points; this is the minimum required to assess any exploit family",
      "command_or_source": "cast 4byte-decode or whatsabi against the deployed bytecode at bsc rpc; alternatively parse the verified ABI from BSCScan"
    },
    {
      "name": "deployer_address_and_funding_source",
      "reason": "deployer_address is empty in the brief; knowing the deployer reveals whether this is a redeployed pattern, a known-bad cluster, or a legitimate protocol; the funding transaction also reveals whether the balance was self-funded (treasury) or user-deposited (custody)",
      "command_or_source": "cast tx $(cast receipt $(cast creation-tx 0x278d858f05b94576c1e6f73285886876ff6ef8d2 --rpc-url $BSC_RPC)) --rpc-url $BSC_RPC | grep from"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "stablecoin_balance tag is present but the specific token(s) and amounts are unknown; needed to confirm the $766k figure and identify the exact asset at risk",
      "command_or_source": "cast call <token> 'balanceOf(address)(uint256)' 0x278d858f05b94576c1e6f73285886876ff6ef8d2 --rpc-url $BSC_RPC for USDT/USDC/BUSD"
    },
    {
      "name": "recent_transaction_history",
      "reason": "immediate_balance_spike tag implies a recent large inflow; tracing the inflow transaction reveals whether funds came from users (deposit pattern) or a single funder (treasury/honeypot pattern), and whether any outflow functions have been called",
      "command_or_source": "https://api.bscscan.com/api?module=account&action=tokentx&address=0x278d858f05b94576c1e6f73285886876ff6ef8d2&sort=desc&apikey=<KEY>"
    }
  ],
  "suspected_exploit_families": [
    "missing access control on value-moving functions",
    "unauthorized withdrawal or sweep",
    "phantom accounting where deposits are accepted but withdrawal is unrestricted"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — not yet resolved",
      "evidence": "no ABI, source, or bytecode analysis present in the repository for this address",
      "why_it_matters": "without at least one confirmed public selector that moves value, no exploit family can be scoped and the candidate cannot advance past NEEDS_LIVE_CONTEXT"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "contract holds ~$766k in stablecoins confirmed by live balance check",
      "at least one public selector exists that transfers or releases tokens",
      "no caller restriction (onlyOwner / whitelist) guards that selector"
    ],
    "call_sequence": [
      "1. identify public withdraw/claim/sweep selector from ABI or bytecode",
      "2. call selector with attacker-controlled recipient address",
      "3. receive stablecoin balance in excess of any deposited entitlement"
    ],
    "expected_gain": "up to ~$766k in stablecoins — contingent on selector discovery and access-control analysis; entirely speculative until live context is retrieved"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC main