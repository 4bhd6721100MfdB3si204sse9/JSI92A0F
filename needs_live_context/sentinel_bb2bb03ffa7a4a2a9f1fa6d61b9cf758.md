<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_d3e5d48d-4a6a-4725-87df-4108d93f7a4f?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

The contract address `0x9996874dbd891c3ecd601eab79d51f92e92d50ee` has no presence anywhere in the repository — no brief, no enrichment artifact, no source, no selectors, no run output.  The `state/latest_targets.json` and all `runs/` artifacts contain no match for this address.  With `verified_source: null`, no deployer, no selectors, and no proxy state, the hard rules require `NEEDS_LIVE_CONTEXT`.

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "",
    "chain": "bsc",
    "address": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "name": "0x9996874dbd891c3ecd601eab79d51f92e92d50ee",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "Fresh, unverified BSC contract holding ~$16.2M TVL in known assets (stablecoin balance confirmed). No source, no selectors, no deployer, and no proxy state are available in any pipeline artifact. The combination of large stablecoin balance, unknown verification status, and zero volume/liquidity is consistent with a custodial or escrow-style contract whose withdrawal surface is entirely unknown.",
  "live_context_required": [
    {
      "name": "bytecode_and_selector_map",
      "reason": "Contract is unverified. Without ABI or bytecode disassembly, no public selectors can be evaluated for unauthorized value movement.",
      "command_or_source": "cast code 0x9996874dbd891c3ecd601eab79d51f92e92d50ee --rpc-url $BSC_RPC | evmdis or heimdall-rs decompile"
    },
    {
      "name": "proxy_and_implementation_check",
      "reason": "Unknown whether this is a proxy. If it is, the implementation address determines the actual attack surface.",
      "command_or_source": "cast storage 0x9996874dbd891c3ecd601eab79d51f92e92d50ee 0x360894a13ba1a3210667c828492db98dca3e2076 --rpc-url $BSC_RPC"
    },
    {
      "name": "token_balance_breakdown",
      "reason": "Tags confirm stablecoin and known-asset balances but do not identify which tokens or amounts. Needed to assess what is extractable.",
      "command_or_source": "bscscan token holdings for 0x9996874dbd891c3ecd601eab79d51f92e92d50ee, or cast call <ERC20> 'balanceOf(address)' 0x9996874dbd891c3ecd601eab79d51f92e92d50ee"
    },
    {
      "name": "deployer_and_funding_trace",
      "reason": "Deployer address is blank. Funding origin determines whether this is a rug-risk custodial contract, a migrator, or a legitimate protocol.",
      "command_or_source": "bscscan internal tx trace for contract creation tx; follow funding wallet cluster"
    },
    {
      "name": "recent_transaction_history",
      "reason": "Zero 24h volume but large balance. Need to confirm whether funds are locked, claimable, or actively moving to assess liveness of any withdrawal path.",
      "command_or_source": "bscscan tx list for 0x9996874dbd891c3ecd601eab79d51f92e92d50ee, last 100 txs"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or redeem (if public withdraw/claim selector exists with no access control)",
    "missing access control on value-moving functions",
    "phantom accounting / unchecked claim (if contract tracks shares or credits without on-chain verification)"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — bytecode not retrieved",
      "evidence": "verified_source is null; no ABI in any pipeline artifact",
      "why_it_matters": "Cannot confirm or deny existence of public withdraw, claim, redeem, or sweep selectors without disassembly"
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract exposes a public withdraw/claim/redeem selector with no caller check",
      "Contract holds stablecoin balance confirmed by live tags"
    ],
    "call_sequence": [
      "1. Disassemble bytecode to recover selector map",
      "2. Identify any value-moving function with no msg.sender guard",
      "3. Call that function with attacker-controlled recipient"
    ],
    "expected_gain": "Up to ~$16.2M in stablecoin/known-asset balance if an unguarded withdrawal path exists — unconfirmed until selectors are known"
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "BSC mainnet fork at current block",
      "Recovered ABI from bytecode disassembly",
      "Attacker EOA with no prior interaction with the contract"
    ],
    "transaction_sequence": [
      "Call candidate public value-moving selector from attacker EOA",
      "Assert attacker token balance increased",
      "Assert contract token balance decreased"
    ],
    "expected_assertions": [
      "attacker.balance(stablecoin) > 0 after call",
      "contract.balance(stablecoin) == 0 or reduced by attacker-controlled amount"
    ]
  },
  "rejection_reason": ""
}
```