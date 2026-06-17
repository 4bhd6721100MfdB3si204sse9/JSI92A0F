from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Candidate:
    source: str
    external_id: str
    name: str
    chain: str
    entity_type: str = "protocol"
    address: str = ""
    category: str = ""
    url: str = ""
    liquidity_usd: float = 0.0
    tvl_usd: float = 0.0
    volume24h_usd: float = 0.0
    fdv_usd: float = 0.0
    price_change_24h_pct: float = 0.0
    verified_source: bool | None = None
    deployer_address: str = ""
    funding_cluster_id: str = ""
    created_at_ms: int | None = None
    tags: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def stable_key(self) -> str:
        chain = self.chain.lower().strip() or "unknown"
        address = self.address.lower().strip()
        if address:
            return f"{chain}:{address}"
        return f"{self.source}:{self.external_id.lower()}"

    def value_at_risk(self) -> float:
        return max(self.liquidity_usd, self.tvl_usd)


@dataclass
class ScoredCandidate:
    candidate: Candidate
    score: int
    reasons: list[str]
    next_action: str

    def as_dict(self) -> dict[str, Any]:
        c = self.candidate
        return {
            "score": self.score,
            "next_action": self.next_action,
            "reasons": self.reasons,
            "source": c.source,
            "external_id": c.external_id,
            "name": c.name,
            "chain": c.chain,
            "entity_type": c.entity_type,
            "address": c.address,
            "category": c.category,
            "url": c.url,
            "liquidity_usd": c.liquidity_usd,
            "tvl_usd": c.tvl_usd,
            "volume24h_usd": c.volume24h_usd,
            "fdv_usd": c.fdv_usd,
            "price_change_24h_pct": c.price_change_24h_pct,
            "verified_source": c.verified_source,
            "deployer_address": c.deployer_address,
            "funding_cluster_id": c.funding_cluster_id,
            "created_at_ms": c.created_at_ms,
            "tags": c.tags,
        }
