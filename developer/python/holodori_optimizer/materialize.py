from __future__ import annotations

from copy import deepcopy
import math


def materialize_card(card: dict, level: int | None = None, bloom: int = 5, key_override: str | None = None) -> dict:
    max_level = int(card["maxLevel"])
    if level is None:
        level = max_level
    level = max(1, min(max_level, int(round(float(level)))))
    bloom = max(0, min(5, int(round(float(bloom)))))
    stage = card["bloomStages"][bloom]
    base = card["levelBaseValues"][level - 1]
    mult = 1 + stage["statBonus"]
    stats = [math.ceil(base * p / 1000 * mult) for p in card["statPermil"]]
    active = deepcopy(card["activeLevels"][str(stage["activeLevel"])])
    passive = deepcopy(card["passiveLevels"][str(stage["passiveLevel"])])
    special = deepcopy(card["specialLevels"][str(stage["specialLevel"])])
    return {
        "id": card["id"],
        "assetId": card.get("assetId"),
        "key": key_override or card["id"],
        "displayKey": f"{card['rarity']}★ {card['member']} | {card['name']}",
        "member": card["member"],
        "skin": card["name"],
        "characterId": card["characterId"],
        "rarity": card["rarity"],
        "attributeId": card["attributeId"],
        "type": card["attribute"],
        "groupIds": list(card.get("groupIds", [])),
        "generation": " / ".join(card.get("groupLabels", [])),
        "perf": stats[0],
        "tech": stats[1],
        "sense": stats[2],
        "total": sum(stats),
        "level": level,
        "bloom": bloom,
        "maxLevel": max_level,
        "passive": passive,
        "outfit": deepcopy(card["outfit"]),
        "active": active,
        "special": special,
    }


def materialize_master(master: dict, progress: dict[str, dict] | None = None) -> list[dict]:
    progress = progress or {}
    out = []
    for card in master["cards"]:
        p = progress.get(card["id"], {})
        out.append(materialize_card(card, p.get("level", card["maxLevel"]), p.get("bloom", 5)))
    return out
