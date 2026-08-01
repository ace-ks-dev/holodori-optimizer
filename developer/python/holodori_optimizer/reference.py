from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from itertools import combinations
import math

COMBO_SPECIAL_WEIGHTS = [0.92, 0.96, 1.00, 1.04, 1.08]
NEUTRAL_SPECIAL_WEIGHTS = [1, 1, 1, 1, 1]


class ReferenceModelError(RuntimeError):
    pass


def _eligible(card: dict, target: dict | None) -> bool:
    if not target:
        return False
    kind = target.get("kind")
    if kind == "all":
        return True
    if kind == "attribute":
        return card.get("attributeId") == target.get("id")
    if kind == "group":
        return target.get("id") in card.get("groupIds", [])
    return False


def trigger_satisfied(trigger: dict | None, cards: list[dict]) -> bool:
    if not trigger:
        return True
    kind = trigger.get("kind")
    if kind in ("attribute", "group"):
        count = sum(1 for c in cards if _eligible(c, {"kind": kind, "id": trigger.get("id")}))
        return count >= int(trigger.get("count") or 1)
    if kind in ("combo_gte", "life_gte", "life_lte", "judgement_gte"):
        return True
    return False


def active_magnitude(card: dict, cards: list[dict]) -> float:
    active = card["active"]
    conditional = active.get("conditionalMagnitude")
    if conditional is not None and trigger_satisfied(active.get("trigger"), cards):
        return float(conditional)
    return float(active.get("baseMagnitude") or 0)


def base_active_probability(card: dict) -> float:
    return max(0.0, min(1.0, float(card.get("active", {}).get("probability") or 0)))


def effective_active_probability(card: dict, sar_multiplier: float = 1.0) -> float:
    return min(1.0, base_active_probability(card) * sar_multiplier)


def _active_windows(card: dict, song: int) -> list[bool]:
    duration = float(card["active"].get("duration") or 0)
    interval = float(card["active"].get("interval") or 0)
    out = [False] * song
    if duration <= 0 or interval <= 0:
        return out
    for t in range(1, song + 1):
        # Mirrors v2.1 worker exactly. Current game intervals/durations are integer seconds.
        if t >= interval and (t % interval) < duration:
            out[t - 1] = True
    return out


def overlap_counts(cards: list[dict], song: int) -> list[int]:
    masks = [_active_windows(c, song) for c in cards]
    counts = [0] * 32
    for subset in range(1, 32):
        n = 0
        for t in range(song):
            ok = True
            for i in range(5):
                if subset & (1 << i) and not masks[i][t]:
                    ok = False
                    break
            if ok:
                n += 1
        counts[subset] = n
    return counts


def passive_recipients(cards: list[dict], source_index: int, passive: dict) -> list[int]:
    if not trigger_satisfied(passive.get("trigger"), cards):
        return []
    target = passive.get("target") or {}
    if target.get("kind") == "self":
        return [source_index]
    eligible = [i for i, card in enumerate(cards) if _eligible(card, target)]
    count = int(target.get("count") or len(eligible))
    if len(eligible) < count:
        return []
    eligible.sort(key=lambda i: (-cards[i]["total"], i))
    return eligible[:count]


def timing(cards: list[dict], counts: list[int], support: list[float], song: int, sar_multiplier: float = 1.0, details: bool = False) -> dict:
    probabilities = [effective_active_probability(c, sar_multiplier) for c in cards]
    magnitudes = [active_magnitude(c, cards) for c in cards]
    priority = sorted(range(5), key=lambda i: (-magnitudes[i], i))
    rank = [0] * 5
    for r, i in enumerate(priority):
        rank[i] = r

    raw = 0.0
    supported = 0.0
    for i in range(5):
        higher = [j for j in range(5) if rank[j] < rank[i]]
        factor = 0.0
        # Inclusion-exclusion over successful higher-magnitude skills.
        for r in range(len(higher) + 1):
            for subset_tuple in combinations(higher, r):
                prod = 1.0
                subset_mask = 1 << i
                for j in subset_tuple:
                    prod *= probabilities[j]
                    subset_mask |= 1 << j
                factor += (-1 if r % 2 else 1) * prod * counts[subset_mask]
        contribution = magnitudes[i] * probabilities[i] * factor / song
        raw += contribution
        supported += contribution * (1 + support[i])

    coverage = 0.0
    for subset in range(1, 32):
        prod = 1.0
        bits = 0
        for j in range(5):
            if subset & (1 << j):
                bits += 1
                prod *= probabilities[j]
        coverage += (1 if bits % 2 else -1) * prod * counts[subset] / song

    out = {"raw": raw, "supported": supported, "coverage": coverage}
    if details:
        out["probabilities"] = probabilities
        out["magnitudes"] = magnitudes
    return out


def special_data(card: dict, cards: list[dict]) -> dict:
    special = card.get("special") or {"magnitude": 0, "duration": 0, "sarPct": 0, "sarTrigger": None, "text": "Not modeled"}
    sar_pct = float(special.get("sarPct") or 0) if float(special.get("sarPct") or 0) > 0 and trigger_satisfied(special.get("sarTrigger"), cards) else 0.0
    return {
        "magnitude": float(special.get("magnitude") or 0),
        "duration": float(special.get("duration") or 0),
        "hasSar": sar_pct > 0,
        "sarPct": sar_pct,
        "text": str(special.get("text") or ""),
    }


def special_for_order(cards: list[dict], song: int, special_mode: str) -> dict:
    if special_mode == "off":
        return {"bonus": 0.0, "values": [], "sarWindows": [], "sarCount": 0}
    weights = NEUTRAL_SPECIAL_WEIGHTS if special_mode == "neutral" else COMBO_SPECIAL_WEIGHTS
    bonus = 0.0
    values = []
    sar_windows = []
    for i, card in enumerate(cards):
        s = special_data(card, cards)
        exposure = min(s["duration"], song) / song
        direct = s["magnitude"] * s["duration"] / song
        weighted = direct * weights[i]
        bonus += weighted
        value = {
            "position": i + 1,
            "member": card["member"],
            "magnitude": s["magnitude"],
            "duration": s["duration"],
            "weight": weights[i],
            "bonus": weighted,
            "hasSar": s["hasSar"],
            "sarPct": s["sarPct"],
            "text": s["text"],
        }
        values.append(value)
        if s["sarPct"] > 0 and s["duration"] > 0:
            sar_windows.append({**value, "exposure": exposure, "multiplier": 1 + s["sarPct"]})
    return {"bonus": bonus, "values": values, "sarWindows": sar_windows, "sarCount": len(sar_windows)}


def sar_for_order(cards: list[dict], counts: list[int], support: list[float], song: int, special_mode: str, sp: dict, base_timing: dict, details: bool = False) -> dict:
    if special_mode == "off" or not sp["sarWindows"]:
        return {"rawUplift": 0.0, "passiveUplift": 0.0, "coverage": base_timing["coverage"], "coverageUplift": 0.0, "values": []}
    raw_uplift = passive_uplift = coverage_uplift = 0.0
    values = []
    for window in sp["sarWindows"]:
        boosted = timing(cards, counts, support, song, window["multiplier"], details)
        raw_delta = (boosted["raw"] - base_timing["raw"]) * window["exposure"] * window["weight"]
        passive_delta = (boosted["supported"] - base_timing["supported"]) * window["exposure"] * window["weight"]
        coverage_delta = (boosted["coverage"] - base_timing["coverage"]) * window["exposure"]
        raw_uplift += raw_delta
        passive_uplift += passive_delta
        coverage_uplift += coverage_delta
        if details:
            values.append({**window, "rawUplift": raw_delta, "passiveUplift": passive_delta, "coverageUplift": coverage_delta, "boostedProbabilities": boosted.get("probabilities")})
    return {
        "rawUplift": raw_uplift,
        "passiveUplift": passive_uplift,
        "coverage": min(1.0, base_timing["coverage"] + coverage_uplift),
        "coverageUplift": coverage_uplift,
        "values": values,
    }


def outfit_bonuses(cards: list[dict], outfit_card: dict, details: bool = False) -> dict:
    perf = tech = sense = all_bonus = support = 0.0
    triggered_count = 0
    effect_details = []
    for effect in (outfit_card.get("outfit") or {}).get("effects", []):
        triggered = trigger_satisfied(effect.get("trigger"), cards)
        if details:
            effect_details.append({"kind": effect.get("kind"), "pct": effect.get("pct"), "triggered": triggered})
        if not triggered:
            continue
        triggered_count += 1
        kind = effect.get("kind")
        pct = float(effect.get("pct") or 0)
        if kind == "perf": perf += pct
        elif kind == "tech": tech += pct
        elif kind == "sense": sense += pct
        elif kind == "all": all_bonus += pct
        elif kind == "support": support += pct
    return {"perf": perf, "tech": tech, "sense": sense, "all": all_bonus, "support": support, "triggeredCount": triggered_count, "details": effect_details}


def _outfit_outcome(cards: list[dict], outfit_card: dict, base_stat: float, sum_perf: float, sum_tech: float, sum_sense: float, tm: dict, sp: dict, sar: dict, other: float, details: bool = False) -> dict:
    bon = outfit_bonuses(cards, outfit_card, details)
    stat = base_stat + sum_perf * (bon["perf"] + bon["all"]) + sum_tech * (bon["tech"] + bon["all"]) + sum_sense * (bon["sense"] + bon["all"])
    baseline_adjusted = tm["supported"] + bon["support"] * tm["raw"]
    sar_uplift = sar["passiveUplift"] + bon["support"] * sar["rawUplift"]
    adjusted = baseline_adjusted + sar_uplift
    support_uplift = baseline_adjusted - tm["raw"]
    total_bonus = adjusted + sp["bonus"] + other
    index = stat * (1 + total_bonus / 100)
    outfit = outfit_card.get("outfit") or {"effects": [], "text": ""}
    return {
        "score": index, "stat": stat, "raw": tm["raw"], "uplift": support_uplift, "sarUplift": sar_uplift,
        "supported": adjusted, "coverage": sar["coverage"], "specialBonus": sp["bonus"], "totalBonus": total_bonus,
        "outfitCard": outfit_card["id"], "outfitKey": outfit_card["key"], "outfitOwner": outfit_card["member"],
        "outfitText": outfit.get("text", ""), "outfitTriggered": bon["triggeredCount"] > 0 or not outfit.get("effects", []),
        "outfitSupport": bon["support"], "outfitExternal": outfit_card["id"] not in {c["id"] for c in cards},
        "outfitEffectDetails": bon["details"],
    }


def unique_outfit_cards(all_cards: list[dict]) -> list[dict]:
    seen = set(); out = []
    import json
    for c in all_cards:
        signature = json.dumps((c.get("outfit") or {}).get("effects", []), separators=(",", ":"), sort_keys=True)
        if signature not in seen:
            seen.add(signature); out.append(c)
    return out


def evaluate_order(ordered_cards: list[dict], *, all_cards: list[dict] | None = None, song: int = 140, special_mode: str = "combo", other: float = 0.0, outfit_mode: str = "team", outfit_id: str | None = None, details: bool = True) -> dict:
    if len(ordered_cards) != 5 or len({c["characterId"] for c in ordered_cards}) != 5:
        raise ReferenceModelError("evaluate_order requires five ordered cards from distinct holomems")
    song = int(song)
    if song <= 0:
        raise ReferenceModelError("song must be positive")
    all_cards = all_cards or ordered_cards
    by_id = {c["id"]: c for c in all_cards}

    perf = [0.0] * 5; tech = [0.0] * 5; sense = [0.0] * 5; all_buff = [0.0] * 5; support = [0.0] * 5
    passive_details = []
    for source_index, src in enumerate(ordered_cards):
        pa = src["passive"]
        recipients = passive_recipients(ordered_cards, source_index, pa)
        if not recipients:
            continue
        for i in recipients:
            kind = pa.get("kind"); pct = float(pa.get("pct") or 0)
            if kind == "support": support[i] += pct
            elif kind == "perf": perf[i] += pct
            elif kind == "tech": tech[i] += pct
            elif kind == "sense": sense[i] += pct
            elif kind == "all": all_buff[i] += pct
        if details:
            passive_details.append(f"{src['member']}: {pa.get('text','')} → {', '.join(ordered_cards[i]['member'] for i in recipients)}")

    base_stat = sum_perf = sum_tech = sum_sense = 0.0
    for i, c in enumerate(ordered_cards):
        sum_perf += c["perf"]; sum_tech += c["tech"]; sum_sense += c["sense"]
        base_stat += c["perf"] * (1 + perf[i] + all_buff[i]) + c["tech"] * (1 + tech[i] + all_buff[i]) + c["sense"] * (1 + sense[i] + all_buff[i])

    counts = overlap_counts(ordered_cards, song)
    sp = special_for_order(ordered_cards, song, special_mode)
    tm = timing(ordered_cards, counts, support, song, 1.0, details)
    sar = sar_for_order(ordered_cards, counts, support, song, special_mode, sp, tm, details)

    team_outcomes = [_outfit_outcome(ordered_cards, c, base_stat, sum_perf, sum_tech, sum_sense, tm, sp, sar, other, details) for c in ordered_cards]
    best_team = max(team_outcomes, key=lambda x: x["score"])
    best_any = best_team
    if outfit_mode == "any":
        best_any = max((_outfit_outcome(ordered_cards, c, base_stat, sum_perf, sum_tech, sum_sense, tm, sp, sar, other, details) for c in unique_outfit_cards(all_cards)), key=lambda x: x["score"])
        used = best_any
    elif outfit_mode == "fixed":
        if not outfit_id or outfit_id not in by_id:
            raise ReferenceModelError("fixed outfit_id is missing or unknown")
        used = _outfit_outcome(ordered_cards, by_id[outfit_id], base_stat, sum_perf, sum_tech, sum_sense, tm, sp, sar, other, details)
        best_any = used
    else:
        used = best_team

    result = dict(used)
    result.update({
        "bestAvailableScore": best_any["score"],
        "bestAvailableOutfitCard": best_any["outfitCard"],
        "bestAvailableOutfitKey": best_any["outfitKey"],
        "bestAvailableOutfitOwner": best_any["outfitOwner"],
        "bestAvailableOutfitText": best_any["outfitText"],
        "bestAvailableOutfitTriggered": best_any["outfitTriggered"],
        "bestAvailableOutfitExternal": best_any["outfitExternal"],
    })
    if details:
        result.update({
            "activeProbabilities": tm.get("probabilities"), "activeMagnitudes": tm.get("magnitudes"),
            "cards": [c.get("displayKey") or f"{c['member']} | {c['skin']}" for c in ordered_cards],
            "cardIds": [c["id"] for c in ordered_cards], "cardKeys": [c["key"] for c in ordered_cards],
            "cardProgress": [{"level": c["level"], "bloom": c["bloom"], "rarity": c["rarity"]} for c in ordered_cards],
            "members": [c["member"] for c in ordered_cards], "passiveDetails": passive_details,
            "support": support, "specialDetails": sp["values"], "sarDetails": sar["values"],
            "sarCount": sp["sarCount"], "coverageUplift": sar["coverageUplift"],
        })
    return result
