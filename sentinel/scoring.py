from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import Candidate, ScoredCandidate


def score_candidate(candidate: Candidate, config: dict[str, Any]) -> ScoredCandidate:
    score = 0
    reasons: list[str] = []
    value = candidate.value_at_risk()
    entity_type = candidate.entity_type.lower().strip() or "protocol"
    is_bot_contract = entity_type == "bot_contract"
    is_unverified_contract = entity_type == "unverified_contract" or candidate.verified_source is False
    is_unknown_protocol = entity_type in {"unknown_protocol", "protocol"}
    tags = set(candidate.tags)

    min_value = float(config.get("min_value_usd", 50_000))
    min_bot_value = float(config.get("min_bot_value_usd", 10_000))
    min_unverified_value = float(config.get("min_unverified_value_usd", 100_000))
    min_spike_value = float(config.get("min_spike_value_usd", 100_000))
    min_cluster_value = float(config.get("min_cluster_value_usd", 50_000))
    if value >= 10_000_000:
        score += 35
        reasons.append(f"value_at_risk>=10000000:{value:.0f}")
    elif value >= 1_000_000:
        score += 25
        reasons.append(f"value_at_risk>=1000000:{value:.0f}")
    elif value >= 250_000:
        score += 16
        reasons.append(f"value_at_risk>=250000:{value:.0f}")
    elif value >= min_value:
        score += 8
        reasons.append(f"value_at_risk>=minimum:{value:.0f}")
    else:
        reasons.append(f"value_below_minimum:{value:.0f}")

    if is_bot_contract:
        bot_weight = int(config.get("bot_contract_weight", 18))
        score += bot_weight
        reasons.append(f"bot_contract:{bot_weight}")

    if is_unverified_contract:
        unverified_weight = int(config.get("unverified_contract_weight", 20))
        score += unverified_weight
        reasons.append(f"unverified_contract:{unverified_weight}")

    chain = candidate.chain.lower()
    chain_weight = int(config.get("chain_weights", {}).get(chain, 0))
    if chain_weight:
        score += chain_weight
        reasons.append(f"chain_weight:{chain}:{chain_weight}")

    surface_text = " ".join(
        [
            candidate.name,
            candidate.category,
            " ".join(candidate.tags),
            str(candidate.raw.get("description", "")),
            str(candidate.raw.get("behavior", "")),
        ]
    ).lower()
    for keyword, weight in config.get("surface_keywords", {}).items():
        if keyword.lower() in surface_text:
            score += int(weight)
            reasons.append(f"surface:{keyword}:{weight}")
            break

    fresh_days = int(config.get("fresh_days", 14))
    if candidate.created_at_ms:
        age_days = _age_days(candidate.created_at_ms)
        if age_days <= 3:
            score += 20
            reasons.append(f"fresh_pair<=3d:{age_days}")
        elif age_days <= fresh_days:
            score += 12
            reasons.append(f"fresh_pair<={fresh_days}d:{age_days}")

    if "latest_profile" in candidate.tags:
        score += 8
        reasons.append("latest_profile")
    if "latest_boost" in candidate.tags:
        score += 10
        reasons.append("latest_boost")
    if "verified_bot_contract" in candidate.tags:
        score += 10
        reasons.append("verified_bot_contract")
    if "high_tx_count" in candidate.tags:
        score += 8
        reasons.append("high_tx_count")
    if "flashloan_user" in candidate.tags:
        score += 10
        reasons.append("flashloan_user")
    if "dex_path_executor" in candidate.tags:
        score += 8
        reasons.append("dex_path_executor")
    if "sudden_price_spike" in tags:
        spike_weight = int(config.get("sudden_spike_weight", 18))
        score += spike_weight
        reasons.append(f"sudden_price_spike:{spike_weight}")
    if "unknown_protocol" in tags:
        unknown_weight = int(config.get("unknown_protocol_weight", 10))
        score += unknown_weight
        reasons.append(f"unknown_protocol:{unknown_weight}")
    if "prior_project_closed" in tags:
        weight = int(config.get("prior_project_closed_weight", 18))
        score += weight
        reasons.append(f"prior_project_closed:{weight}")
    if "same_deployer_closed_project" in tags:
        weight = int(config.get("same_deployer_closed_project_weight", 22))
        score += weight
        reasons.append(f"same_deployer_closed_project:{weight}")
    if "funding_from_closed_project" in tags:
        weight = int(config.get("funding_from_closed_project_weight", 24))
        score += weight
        reasons.append(f"funding_from_closed_project:{weight}")
    if "suspected_rug_redeploy" in tags:
        weight = int(config.get("suspected_rug_redeploy_weight", 28))
        score += weight
        reasons.append(f"suspected_rug_redeploy:{weight}")
    if _has_proxy_change_live_funds(tags):
        weight = int(config.get("proxy_change_live_funds_weight", 26))
        score += weight
        reasons.append(f"proxy_change_live_funds:{weight}")
    if _has_reward_pool_claimability(tags):
        weight = int(config.get("reward_pool_claimability_weight", 24))
        score += weight
        reasons.append(f"reward_pool_claimability:{weight}")
    if _has_bridge_escrow_risk(tags):
        weight = int(config.get("bridge_escrow_weight", 24))
        score += weight
        reasons.append(f"bridge_escrow:{weight}")
    if _has_approval_router_risk(tags):
        weight = int(config.get("approval_router_weight", 22))
        score += weight
        reasons.append(f"approval_router:{weight}")
    if _has_vault_share_asset_risk(tags):
        weight = int(config.get("vault_share_asset_weight", 24))
        score += weight
        reasons.append(f"vault_share_asset:{weight}")
    if _has_lending_oracle_liquidation_risk(tags):
        weight = int(config.get("lending_oracle_liquidation_weight", 24))
        score += weight
        reasons.append(f"lending_oracle_liquidation:{weight}")

    spike_threshold = float(config.get("price_spike_24h_pct", 100))
    if candidate.price_change_24h_pct >= spike_threshold:
        score += int(config.get("price_spike_weight", 18))
        reasons.append(f"price_spike_24h>={spike_threshold:.0f}:{candidate.price_change_24h_pct:.0f}")

    if candidate.fdv_usd and value and candidate.fdv_usd > 0:
        value_to_fdv = value / candidate.fdv_usd
        if value_to_fdv >= 0.15:
            score += 8
            reasons.append(f"high_liquidity_to_fdv:{value_to_fdv:.2f}")

    mainstream_value = float(config.get("mainstream_value_usd", 100_000_000))
    mainstream_source = candidate.source == "defillama_protocols"
    fresh_or_launch = bool({"latest_profile", "latest_boost"}.intersection(candidate.tags))
    if mainstream_source and value >= mainstream_value and not fresh_or_launch:
        score = max(score - 35, 0)
        reasons.append(f"mainstream_dampener>={mainstream_value:.0f}")

    if is_bot_contract:
        low_value_floor = min_bot_value
    elif _has_cluster_risk(tags):
        low_value_floor = min_cluster_value
    elif is_unverified_contract:
        low_value_floor = min_unverified_value
    elif _has_price_spike(candidate, config) and is_unknown_protocol:
        low_value_floor = min_spike_value
    else:
        low_value_floor = min_value
    if value < low_value_floor:
        score = min(score, 19)
        reasons.append("low_value_score_cap")

    if _has_proxy_change_live_funds(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "proxy_change_live_funds"
    elif _has_reward_pool_claimability(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "reward_pool_claimability_check"
    elif _has_bridge_escrow_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "bridge_escrow_message_validation_check"
    elif _has_approval_router_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "approval_router_drain_surface"
    elif _has_vault_share_asset_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "vault_share_asset_invariant_check"
    elif _has_lending_oracle_liquidation_risk(tags) and value >= min_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "lending_oracle_liquidation_check"
    elif _has_cluster_risk(tags) and value >= min_cluster_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "investigate_redeploy_funding_cluster"
    elif is_unverified_contract and value >= min_unverified_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "reverse_engineer_unverified_funded_contract"
    elif _has_price_spike(candidate, config) and is_unknown_protocol and value >= min_spike_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "price_spike_recon_then_source_check"
    elif is_bot_contract and value >= min_bot_value and score >= int(config.get("queue_threshold", 35)):
        next_action = "trace_bot_contract_then_target_protocols"
    elif is_bot_contract and value < min_bot_value:
        next_action = "watch_bot_contract"
    elif mainstream_source and value >= mainstream_value and not fresh_or_launch:
        next_action = "watch_mainstream"
    elif value >= min_value and score < int(config.get("queue_threshold", 35)):
        next_action = "watch"
    elif value < min_value:
        next_action = "drop_low_value"
    else:
        next_action = "recon_bravo_then_corecritical"

    return ScoredCandidate(candidate=candidate, score=score, reasons=reasons, next_action=next_action)


def _age_days(created_at_ms: int) -> int:
    created = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return max((now - created).days, 0)


def _has_price_spike(candidate: Candidate, config: dict[str, Any]) -> bool:
    threshold = float(config.get("price_spike_24h_pct", 100))
    return "sudden_price_spike" in candidate.tags or candidate.price_change_24h_pct >= threshold


def _has_cluster_risk(tags: set[str]) -> bool:
    return bool(
        {
            "prior_project_closed",
            "same_deployer_closed_project",
            "funding_from_closed_project",
            "suspected_rug_redeploy",
        }.intersection(tags)
    )


def _has_proxy_change_live_funds(tags: set[str]) -> bool:
    return bool({"proxy_impl_changed", "implementation_changed", "live_proxy_funds", "proxy_admin_changed"}.intersection(tags))


def _has_reward_pool_claimability(tags: set[str]) -> bool:
    return bool({"active_reward_pool", "large_claimable_rewards", "reward_pool", "emission_controller"}.intersection(tags))


def _has_bridge_escrow_risk(tags: set[str]) -> bool:
    return bool({"bridge_escrow", "message_validation", "cross_chain_claim", "failed_message_queue"}.intersection(tags))


def _has_approval_router_risk(tags: set[str]) -> bool:
    return bool({"approval_router", "many_user_approvals", "permit_router", "migration_router"}.intersection(tags))


def _has_vault_share_asset_risk(tags: set[str]) -> bool:
    return bool({"share_asset_imbalance", "vault_exchange_rate", "asset_share_drift", "rounding_amplification"}.intersection(tags))


def _has_lending_oracle_liquidation_risk(tags: set[str]) -> bool:
    return bool({"stale_oracle", "new_collateral", "thin_liquidity_lending", "liquidation_path"}.intersection(tags))
