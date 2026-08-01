from __future__ import annotations

import json
from copy import deepcopy


def _intern(value, values: list, index: dict[str, int]) -> int:
    key = json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    if key not in index:
        index[key] = len(values)
        values.append(deepcopy(value))
    return index[key]


def pack_master(master: dict) -> dict:
    """Deduplicate repeated level curves/Bloom profiles for embedding in HTML."""
    level_curves: list[list[int]] = []
    bloom_profiles: list[list[dict]] = []
    level_index: dict[str, int] = {}
    bloom_index: dict[str, int] = {}
    packed_cards = []

    omit = {"key", "attribute", "groupLabels", "levelBaseValues", "bloomStages"}
    for card in master["cards"]:
        c = {k: deepcopy(v) for k, v in card.items() if k not in omit}
        c["levelCurve"] = _intern(card["levelBaseValues"], level_curves, level_index)
        c["bloomProfile"] = _intern(card["bloomStages"], bloom_profiles, bloom_index)
        packed_cards.append(c)

    return {
        "schemaVersion": master["schemaVersion"],
        "source": master["source"],
        "sourceVersion": master["sourceVersion"],
        "groupLabels": deepcopy(master["groupLabels"]),
        "attributeLabels": deepcopy(master["attributeLabels"]),
        "counts": deepcopy(master["counts"]),
        "cards": packed_cards,
        "levelCurves": level_curves,
        "bloomProfiles": bloom_profiles,
    }


def inflate_master(packed: dict) -> dict:
    cards = []
    for card in packed["cards"]:
        c = deepcopy(card)
        c["key"] = f"{c['member']} | {c['name']}"
        c["attribute"] = packed["attributeLabels"].get(c["attributeId"], c["attributeId"])
        c["groupLabels"] = [packed["groupLabels"].get(g, g) for g in c.get("groupIds", [])]
        c["levelBaseValues"] = deepcopy(packed["levelCurves"][c.pop("levelCurve")])
        c["bloomStages"] = deepcopy(packed["bloomProfiles"][c.pop("bloomProfile")])
        cards.append(c)
    return {
        "schemaVersion": packed["schemaVersion"],
        "source": packed["source"],
        "sourceVersion": packed["sourceVersion"],
        "cards": cards,
        "groupLabels": deepcopy(packed["groupLabels"]),
        "attributeLabels": deepcopy(packed["attributeLabels"]),
        "counts": deepcopy(packed["counts"]),
    }
