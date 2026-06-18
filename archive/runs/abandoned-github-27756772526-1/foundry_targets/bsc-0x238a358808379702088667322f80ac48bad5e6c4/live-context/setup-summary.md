# Live Setup Summary

- generated_at: `2026-06-17T13:41:08.847778+00:00`
- target: `0x238a358808379702088667322f80aC48bAd5e6c4`
- label: `Pancakeswap: Infinity Vault`
- contract: `Vault`
- owner: `0xfa206DAB60c014bEb6833004D8848910165e6047`
- owner contract: `GnosisSafeProxy`
- source: BscScan HTML embedded verified source, because anonymous Etherscan v2 API returned `Missing/Invalid API Key`.
- abi_functions: `32`
- priority_selectors_present: `burn, clear, collectFee, mint, registerApp, setOperator, settle, settleFor, take, transfer, transferFrom`

## Recent Method Counts

```json
{
  "0x3655a36a": {
    "revert": 2,
    "success": 0
  },
  "0xcc9c3987": {
    "revert": 1,
    "success": 0
  },
  "Approve": {
    "revert": 0,
    "success": 2
  },
  "Collect Fee": {
    "revert": 5,
    "success": 0
  },
  "Lock": {
    "revert": 1,
    "success": 0
  },
  "Mint": {
    "revert": 1,
    "success": 0
  },
  "Set Operator": {
    "revert": 1,
    "success": 2
  },
  "Sync": {
    "revert": 0,
    "success": 3
  },
  "Take": {
    "revert": 6,
    "success": 0
  },
  "Transfer From": {
    "revert": 1,
    "success": 0
  }
}
```

## Next Audit Focus

The current code model is PancakeSwap Infinity Vault accounting. Public `take`, `clear`, `mint`, `burn`, `collectFee`, `settle`, and transfer methods exist, but exploitability depends on locker/app/operator state and whether a caller can create positive currency deltas beyond entitlement.
