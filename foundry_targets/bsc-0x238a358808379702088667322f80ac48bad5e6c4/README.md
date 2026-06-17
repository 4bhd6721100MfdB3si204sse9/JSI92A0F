# Foundry Target: proof_gate_1451142487af4e99a058662d18c29657

Chain: `bsc`
Target: `0x238a358808379702088667322f80ac48bad5e6c4`
Route: ``

## Setup

```bash
forge install foundry-rs/forge-std
cp .env.example .env
# edit .env and set RPC_URL
forge test -vvv
forge script script/Snapshot.s.sol --rpc-url "$RPC_URL"
```

## What This Repo Contains

- `addresses.json`: target identity and route
- `live_state.json`: Sentinel/DeepWiki context and known live limitations
- `balances.json`: known value-at-risk data plus fields to fill from RPC
- `token_balances.json`: token balances from enrichment when available
- `proxy.json`: EIP-1967 implementation/admin slots and known proxy data
- `abis/Target.json`: verified ABI when available
- `test/LiveStateProof.t.sol`: first fork sanity checks
- `script/Snapshot.s.sol`: basic live snapshot script

## Important Limitation

Private mappings and structs cannot be fully enumerated from chain state unless keys are known. Recover keys from events, calldata, getters, source logic, and prior transactions, then add focused tests.
