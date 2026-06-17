# Known Public Protocol Quarantine

This folder records candidates removed from active DeepWiki/proof queues because the scanner later identified them as popular public protocols, not unknown high-fund bounty targets.

## 2026-06-17

- `0x238a358808379702088667322f80ac48bad5e6c4` is PancakeSwap Infinity Vault on BSC.
- Active queue artifacts were moved to:
  - `deepwiki_pending/rejected_known_public/001-bsc-0x238a358808379702088667322f80ac48bad5e6c4.json`
  - `proof_gate_pending/rejected_known_public/sentinel_590a5c57fea6438184e8b6062dfaf152.md`
- Root cause fixed in `sentinel/chain_scanner.py` and `sentinel/scoring.py`: known public protocols are now tagged as `known_public_protocol` / `known_protocol` and routed to `watch_known_protocol` instead of recon/proof queues.
