<!-- deepwiki_source_url: https://deepwiki.com/search/-deepwiki-sentinel-candidate-t_5f28367c-57da-4881-80f8-16ceb179773b?mode=deep -->
<!-- deepwiki_verdict: needs_live_context -->

```json
{
  "schema_version": "sentinel-triage-v1",
  "verdict": "NEEDS_LIVE_CONTEXT",
  "candidate": {
    "source_file": "explorer_snapshot",
    "chain": "bsc",
    "address": "0x346575fc7f07e6994d76199e41d13dc1575322e1",
    "name": "0x346575fc7f07e6994d76199e41d13dc1575322e1",
    "entity_type": "unknown_protocol",
    "next_action": "recon_bravo_then_corecritical",
    "score": 93
  },
  "paid_scope_match": "fund_extraction",
  "why_this_target_matters": "BSC contract tagged token_funded_contract with a reported $47.38B token balance, zero liquidity, zero FDV, and zero volume. The combination of high_token_balance + zero liquidity is the primary ambiguity: the balance is either phantom (illiquid/worthless token) or real (liquid asset held off-market). No source, no selectors, no deployer, and unknown_verification_status mean no exploit family can be assessed without live enrichment. If the token balance is in a liquid asset (USDT, USDC, WBNB, BTCB), this is a critical fund-extraction target. If the token is illiquid with no DEX pair, this is a reject.",
  "live_context_required": [
    {
      "name": "token_identity_and_liquidity",
      "reason": "The entire $47.38B value claim rests on token balances. The token address(es), symbol(s), decimals, and whether they have real DEX liquidity must be confirmed before any exploit path can be assessed. Zero liquidity_usd and zero volume strongly suggest phantom value, but must be verified.",
      "command_or_source": "cast call 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC | BscScan tokentx API: https://api.bscscan.com/api?module=account&action=tokentx&address=0x346575fc7f07e6994d76199e41d13dc1575322e1&apikey={key}"
    },
    {
      "name": "bytecode_and_selectors",
      "reason": "No ABI or verified source exists. Bytecode must be fetched and 4-byte selectors extracted to determine whether any public value-moving functions (withdraw, claim, transfer, sweep, redeem) are callable by an unprivileged address.",
      "command_or_source": "cast code 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC | python3 -c 'import sys; b=bytes.fromhex(sys.stdin.read().strip()[2:]); [print(b[i:i+4].hex()) for i in range(0,len(b)-3) if b[i]==0x63]' | lookup via https://www.4byte.directory/"
    },
    {
      "name": "deployer_and_creation_tx",
      "reason": "deployer_address is empty. The deployer identity is needed to check for redeploy cluster membership, closed-project funding, or known exploit actor patterns.",
      "command_or_source": "BscScan contract creation: https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0x346575fc7f07e6994d76199e41d13dc1575322e1&apikey={key}"
    },
    {
      "name": "verification_status_and_source",
      "reason": "verified_source is null (unknown), not confirmed false. If source is available, it must be fetched to identify function signatures, access control, and value-moving paths.",
      "command_or_source": "BscScan source code API: https://api.bscscan.com/api?module=contract&action=getsourcecode&address=0x346575fc7f07e6994d76199e41d13dc1575322e1&apikey={key}"
    },
    {
      "name": "proxy_implementation_slot",
      "reason": "Contract may be a proxy. EIP-1967 implementation and admin slots must be checked to determine if a live implementation holds the value-moving logic.",
      "command_or_source": "cast storage 0x346575fc7f07e6994d76199e41d13dc1575322e1 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $BSC_RPC && cast storage 0x346575fc7f07e6994d76199e41d13dc1575322e1 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url $BSC_RPC"
    }
  ],
  "suspected_exploit_families": [
    "unauthorized withdrawal or sweep of token balance",
    "missing access control on value-moving public selector",
    "phantom accounting where token balance is withdrawable without deposit record"
  ],
  "source_or_selector_basis": [
    {
      "selector_or_function": "unknown — no ABI or verified source",
      "evidence": "verified_source is null; no selectors present in candidate brief; bytecode not yet fetched",
      "why_it_matters": "Cannot assess any exploit family without knowing the public interface. This is the primary blocker for escalation or rejection."
    },
    {
      "selector_or_function": "token_funded_contract tag",
      "evidence": "Tag is set by chain_scanner._tags() when discovery_source == 'erc20_transfer_log', meaning real ERC20 transfers were observed into this address",
      "why_it_matters": "Confirms real on-chain token transfers occurred. The contract received tokens from an external address. If those tokens are liquid, the balance is real and extractable if access control is absent."
    }
  ],
  "attacker_path_hypothesis": {
    "actor": "unprivileged external user",
    "preconditions": [
      "Contract holds liquid ERC20 tokens (USDT, USDC, WBNB, or BTCB) — not yet confirmed",
      "At least one public selector exists that moves tokens to an arbitrary caller-controlled address",
      "No access control (onlyOwner, whitelist, merkle proof) gates the value-moving function"
    ],
    "call_sequence": [
      "1. Identify token address(es) held by 0x346575fc7f07e6994d76199e41d13dc1575322e1 via tokentx API",
      "2. Confirm token has real DEX liquidity (non-zero pair on PancakeSwap or similar)",
      "3. Fetch bytecode and extract 4-byte selectors",
      "4. Match selectors against withdraw/claim/sweep/transfer function signatures",
      "5. Attempt staticcall to any matching selector with attacker address as argument",
      "6. If call succeeds and returns non-zero, attempt live call on fork"
    ],
    "expected_gain": "Unknown until token identity and selectors are confirmed. If liquid tokens are held and a public sweep/withdraw selector exists without access control, gain equals full token balance at market price."
  },
  "local_proof_required": {
    "test_type": "fork",
    "setup": [
      "Fork BSC at current block: anvil --fork-url $BSC_RPC --fork-block-number latest",
      "Confirm token balance: cast call <token_address> 'balanceOf(address)(uint256)' 0x346575fc7f07e6994d76199e41d13dc1575322e1 --rpc-url $BSC_RPC",
      "Confirm token is liquid: check PancakeSwap pair for token/WBNB or token/USDT"
    ],
    "transaction_sequence": [
      "vm.startPrank(attacker) — unprivileged EOA with no prior deposits",
      "target.call(abi.encodeWithSelector(<sweep_or_withdraw_selector>, attacker)) — selector TBD from bytecode analysis",
      "assertGt(IERC20(token).balanceOf(attacker), 0)"
    ],
    "expected_assertions": [
      "attacker token balance increases from 0 to > 0 after call",
      "contract token balance decreases by matching amount",
      "no revert due to access control"
    ]
  },
  "rejection_reason": ""
}
```

**Triage rationale (not part of output):**

The verdict is `NEEDS_LIVE_CONTEXT` rather than `REJECT` for one specific reason: the `token_funded_contract` tag confirms real ERC20 transfers into this address occurred on-chain. The $47.38B figure with `liquidity_usd: 0` and `volume24h_usd: 0` is a strong signal of phantom value (illiquid token), but it is not confirmed. If the held token is USDT, USDC, WBNB, or BTCB — all of which are in the BSC known-token list in `sentinel/chain_scanner.py` — the value is real and the absence of selectors/source becomes the critical gap. The five live-context items above are the minimum needed to either escalate to `NEEDS_LOCAL_PROOF` or issue a `REJECT`.