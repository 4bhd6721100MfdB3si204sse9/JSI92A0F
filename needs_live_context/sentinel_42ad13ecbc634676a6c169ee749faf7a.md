<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_106a00a6-a30c-42a9-ba7c-51bfa114ae00?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract `0x585d44727129b9c69791b10238ca605932938b4f` does not appear anywhere in the repository's state files, deepwiki briefs, chain scanner records, or run artifacts. All enrichment data in the repo uses placeholder addresses. There is no source code, ABI, selector list, deployer info, proxy state, or transaction history available for this address. Per the hard rules, this is `NEEDS_LIVE_CONTEXT`.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "ethereum",
    "address": "0x585d44727129b9c69791b10238ca605932938b4f",
    "name": "0x585d44727129b9c69791b10238ca605932938b4f",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 89
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh Ethereum contract with ~$458K TVL, an immediate balance spike, and no verified source. The combination of hidden_high_value_contract + balance_spike + unknown_verification_status on a token-funded contract is a high-signal pattern for unauthorized withdrawal or phantom accounting risk. No source, ABI, selectors, deployer, or proxy state are available in the current pipeline artifacts, so exploitability cannot be assessed without live enrichment.",
  "live_context_required": [
    {
      "name": "contract_bytecode_and_source",
      "reason": "verified_source is null; without ABI or decompiled selectors there is no way to identify value-moving entry points or access control gaps",
      "command_or_source": "cast code 0x585d44727129b9c69791b10238ca605932938b4f --rpc-url $ETH_RPC; etherscan API /api?module=contract&action=getsourcecode&address=0x585d44727129b9c69791b10238ca605932938b4f"
    },
    {
      "name": "proxy_and_implementation_state",
      "reason": "unknown whether this is a proxy; if it is, the implementation slot determines the actual logic and any recent upgrade is a critical signal",
      "command_or_source": "cast storage 0x585d44727129b9c69791b10238ca605932938b4f 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $ETH_RPC"
    },
    {
      "name": "token_balances_and_asset_identity",
      "reason": "tags indicate token_funded_contract and high_token_balance but the specific ERC-20(s) held are unknown; asset identity determines whether the TVL is liquid and extractable",
      "command_or_source": "etherscan API /api?module=account&action=tokenlist&address=0x585d44727129b9c69791b10238ca605932938b4f; cast call <token> 'balanceOf(address)' 0x585d44727129b9c69791b10238ca605932938b4f --rpc-url $ETH_RPC"
    },
    {
      "name": "deployer_address_and_funding_cluster",
      "reason": "deployer_address is empty; tracing the deployer reveals whether this is a redeploy from a closed project, a known rug pattern, or a bot-funded contract",
      "command_or_source": "cast tx $(cast receipt $(cast find-block --rpc-url $ETH_RPC) --rpc-url $ETH_RPC) --rpc-url $ETH_RPC; etherscan API /api?module=contract&action=getcontractcreation&contractaddresses=0x585d44727129b9c69791b10238ca605932938b4f"
    },
    {
      "name": "public_selector_enumeration",
      "reason": "without selectors there is no way to identify withdraw, redeem, claim, sweep, or migrate entry points accessible to an unprivileged caller",
      "command_or_source": "heimdall decompile 0x585d44727129b9c69791b10238ca605932938b4f; 4byte.directory lookup on extracted 4-byte selectors from bytecode"
    },
    {
      "name": "recent_transaction_history",
      "reason": "balance_spike and immediate_balance_spike tags require confirmation of the funding transaction(s) and any subsequent outflows to assess whether funds are still present and claimable",
      "command_or_source": "etherscan API /api?module=account&action=txlist&address=0x585d44727129b9c69791b10238ca605932938b4f&sort=desc; cast logs --address 0x585d44727129b9c69791b10238ca605932938b4f --rpc-url $ETH_RPC"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or redeem (missing access control on value-moving selectors)",
    "phantom accounting (shares or claims created without matching deposited assets)",
    "missing access control on sweep or migrate function",
    "proxy or implementation mismatch exposing live funds"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or source available",
      "evidence": "verified_source is null; bytecode not yet decompiled in pipeline artifacts",
      "why_it_matters": "Cannot confirm or deny the existence of unprivileged withdraw/claim/sweep selectors without this step"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds ~$458K in token(s) confirmed by live balance check",
      "At least one public selector exists that moves tokens to an arbitrary recipient or to msg.sender without ownership/role check",
      "No timelock, merkle proof, or per-user accounting prevents a cold-call extraction"
    ],
    "call_sequence": [
      "1. Identify value-moving selectors via bytecode decompilation",
      "2. Check each selector for msg.sender access control (owner, role, whitelist)",
      "3. If unchecked: call selector directly from an EOA with no prior deposit",
      "4. Observe token transfer to attacker address"
    ],
    "expected_gain": "Up to ~$458K in held tokens if an unguarded withdrawal or sweep path exists — unconfirmable without source/selectors"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Obtain ABI or decompiled selectors from live bytecode",
      "Pin Ethereum mainnet fork at the block where balance spike occurred",
      "Identify the token contract(s) held and their decimals"
    ],
    "transaction_sequence": [
      "vm.startPrank(address(0xdead)) — unprivileged EOA with no prior interaction",
      "Call candidate value-moving selector(s) identified from decompilation",
      "Assert token balance of attacker address increased"
    ],
    "expected_assertions": [
      "attacker token balance after > attacker token balance before",
      "contract token balance after < contract token balance before",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Key blocker:** The address `0x585d44727129b9c69791b10238ca605932938b4f` has no entry in any pipeline artifact in this repository — not in `state/ethereum_chain_scanner.json`, `state/latest_targets.json`, `state/latest_deepwiki_briefs.json`, or any `deepwiki_briefs/` file. [1](#0-0) [2](#0-1)  The pipeline's Live Enrichment stage (Stage 3) has not yet run for this address, meaning no source, proxy slot, deployer, or selector data has been fetched. [3](#0-2)  Until those six live-context items are resolved, the gate question cannot be answered and the candidate must remain `NEEDS_LIVE_CONTEXT`.

### Citations

**File:** state/latest_deepwiki_briefs.json (L1-5)
```json
[
  "deepwiki_briefs/001-bsc-0x7777777777777777777777777777777777777777.json",
  "deepwiki_briefs/002-bsc-0x5555555555555555555555555555555555555555.json",
  "deepwiki_briefs/003-base-0x6666666666666666666666666666666666666666.json"
]
```

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

**File:** DEEPWIKI_SENTINEL_WORKFLOW_PLAN.md (L125-144)
```markdown
### Stage 3 - Live Enrichment

Run:

```bash
python3 -m sentinel discover --source explorer_live --input examples/live_targets.json --limit "${SENTINEL_LIMIT:-50}"
```

Output:

- enriched `runs/<timestamp>/candidates_scored.json`
- enriched `triage_queue.*`
- `state/latest_live_snapshot.json`

Required upgrade:

- persist the raw explorer snapshot separately before scoring
- include commands/API URLs used, block number, chain id, balance source, and timestamp
- mark stale live data as unusable after a configured TTL

```