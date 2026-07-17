from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from .models import Candidate

PREFERRED_CHAINS = {"ethereum", "eth", "mainnet", "bsc", "bnb", "binance-smart-chain"}
KNOWN_PUBLIC_HINTS = {
    "pancakeswap",
    "pancake swap",
    "uniswap",
    "aave",
    "curve",
    "balancer",
    "compound",
    "yearn",
    "venus",
}
VALUABLE_ROLES = {
    "vault",
    "staking",
    "rewards",
    "reward",
    "router",
    "migration",
    "bridge",
    "bridge_escrow",
    "escrow",
    "lending",
    "oracle",
    "liquidation",
    "treasury",
    "strategy",
    "farm",
}


@dataclass
class VerifiedAddressFinding:
    id: str
    chain: str
    address: str
    project: str
    explorer_url: str
    verified_source: bool
    source_url: str
    contract_role: str
    value_usd: float
    disclosure_path: str
    audit_evidence: str
    known_public_risk: str
    why_interesting: str
    recommended_next_action: str
    confidence: str
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _norm_chain(chain: str) -> str:
    c = (chain or "").strip().lower()
    if c in {"eth", "mainnet"}:
        return "ethereum"
    if c in {"bnb", "binance-smart-chain"}:
        return "bsc"
    return c


def _raw(candidate: Candidate, key: str, default: Any = "") -> Any:
    return (candidate.raw or {}).get(key, default)


def _has_disclosure_path(candidate: Candidate) -> bool:
    raw = candidate.raw or {}
    for key in ("bounty_url", "security_url", "disclosure_url", "security_contact", "program_url"):
        if str(raw.get(key, "")).strip():
            return True
    tags = {str(t).lower() for t in candidate.tags}
    return bool(tags & {"bug_bounty", "security_page", "responsible_disclosure", "disclosure_path"})


def _known_public_risk(candidate: Candidate) -> str:
    text = " ".join([candidate.name, candidate.category, " ".join(candidate.tags)]).lower()
    if any(hint in text for hint in KNOWN_PUBLIC_HINTS):
        return "high"
    if "known_public_protocol" in text or "popular_protocol" in text:
        return "high"
    if "defillama" in text and candidate.value_at_risk() > 100_000_000:
        return "medium"
    return "low"


def evaluate_verified_address(candidate: Candidate, min_value_usd: float = 250_000) -> VerifiedAddressFinding | None:
    """Return a verified-address finding if the candidate passes Locator's lane.

    This lane is intentionally strict: verified source, ETH/BSC, meaningful value,
    and a disclosure/bounty path are required. Known-public/famous deployments are
    quarantined unless the caller tags them as a fresh unique component.
    """
    reasons: list[str] = []
    chain = _norm_chain(candidate.chain)
    value = float(candidate.value_at_risk() or _raw(candidate, "value_usd", 0) or 0)
    role = (candidate.category or candidate.entity_type or _raw(candidate, "contract_role", "other") or "other").strip().lower()
    tags = {str(t).lower() for t in candidate.tags}

    if chain not in {"ethereum", "bsc"}:
        return None
    reasons.append("preferred_chain")

    if candidate.verified_source is not True:
        return None
    reasons.append("verified_source")

    if not candidate.address:
        return None
    reasons.append("address_present")

    if value < min_value_usd:
        return None
    reasons.append(f"value_usd>={int(min_value_usd)}")

    if not _has_disclosure_path(candidate):
        return None
    reasons.append("disclosure_path_present")

    known_public_risk = _known_public_risk(candidate)
    fresh_exception = bool(tags & {"fresh_component", "new_deployment", "unique_component", "fresh_unique_component"})
    if known_public_risk == "high" and not fresh_exception:
        return VerifiedAddressFinding(
            id=candidate.stable_key(),
            chain=chain,
            address=candidate.address,
            project=candidate.name,
            explorer_url=candidate.url,
            verified_source=True,
            source_url=str(_raw(candidate, "source_url", candidate.url)),
            contract_role=role,
            value_usd=value,
            disclosure_path=str(_raw(candidate, "bounty_url", _raw(candidate, "security_url", _raw(candidate, "disclosure_url", "")))),
            audit_evidence=str(_raw(candidate, "audit_evidence", "unknown")),
            known_public_risk=known_public_risk,
            why_interesting="Known-public/crowded target; do not promote without a fresh unique component.",
            recommended_next_action="known_public_quarantine",
            confidence="high",
            reasons=reasons + ["known_public_quarantine"],
        )

    if role in VALUABLE_ROLES or tags & VALUABLE_ROLES:
        reasons.append("valuable_contract_role")

    confidence = "high" if value >= 1_000_000 and known_public_risk == "low" else "medium"
    why = "Verified-source high-value contract with disclosure path and under-crowded target profile."
    if fresh_exception:
        why = "Fresh/unique component with verified source, value evidence, and disclosure path despite known-public name risk."

    return VerifiedAddressFinding(
        id=candidate.stable_key(),
        chain=chain,
        address=candidate.address,
        project=candidate.name,
        explorer_url=candidate.url,
        verified_source=True,
        source_url=str(_raw(candidate, "source_url", candidate.url)),
        contract_role=role,
        value_usd=value,
        disclosure_path=str(_raw(candidate, "bounty_url", _raw(candidate, "security_url", _raw(candidate, "disclosure_url", "")))),
        audit_evidence=str(_raw(candidate, "audit_evidence", "none_found")),
        known_public_risk=known_public_risk,
        why_interesting=why,
        recommended_next_action="shadow_value_verified_contract_recon",
        confidence=confidence,
        reasons=reasons,
    )


def find_verified_addresses(candidates: Iterable[Candidate], min_value_usd: float = 250_000) -> list[VerifiedAddressFinding]:
    findings = []
    for candidate in candidates:
        finding = evaluate_verified_address(candidate, min_value_usd=min_value_usd)
        if finding is not None:
            findings.append(finding)
    findings.sort(key=lambda f: (f.recommended_next_action != "shadow_value_verified_contract_recon", -f.value_usd, f.chain, f.address))
    return findings
