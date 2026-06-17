# PancakeSwap Infinity Vault Live Foundry Target

Target: `0x238a358808379702088667322f80aC48bAd5e6c4`
Owner: `0xfa206DAB60c014bEb6833004D8848910165e6047` (`GnosisSafeProxy`)
Chain: `bsc`

This folder is a live Foundry project for the BSC PancakeSwap Infinity Vault. The verified Vault source and ABI were extracted from the BscScan page HTML and stored locally so fork tests can be added without depending on the explorer UI.

## Files

- `src/`: verified Vault source tree from BscScan.
- `source-artifacts/`: raw BscScan contract JSON, copied HTML evidence, and owner proxy source.
- `abis/Vault.json`: live verified ABI.
- `live-context/recent-transactions.json`: recent BscScan transaction table snapshot.
- `test/VaultLiveAuth.t.sol`: first fork tests for live authorization boundaries.
- `script/VaultSnapshot.s.sol`: live read-only snapshot helper.

## Run

```bash
cp .env.example .env
# set RPC_URL or BSC_RPC_URL to a BSC mainnet RPC
forge test -vvv
forge script script/VaultSnapshot.s.sol --rpc-url "$RPC_URL"
```
