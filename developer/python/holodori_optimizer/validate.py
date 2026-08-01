from __future__ import annotations

from collections import Counter
from typing import Any


class ValidationError(RuntimeError):
    pass


def validate_master(master: dict, *, min_cards: int = 100, min_five_star: int = 50) -> dict:
    if not isinstance(master, dict) or master.get("schemaVersion") not in (1, 2):
        raise ValidationError("Normalized HolodoriDB snapshot has an unsupported schemaVersion")
    cards = master.get("cards")
    if not isinstance(cards, list) or len(cards) < min_cards:
        raise ValidationError("Normalized HolodoriDB snapshot is incomplete")

    ids = set()
    character_ids = set()
    five = 0
    for c in cards:
        cid = c.get("id")
        if not cid or cid in ids:
            raise ValidationError(f"Duplicate or missing card id: {cid}")
        ids.add(cid)
        if not c.get("characterId"):
            raise ValidationError(f"Missing characterId: {cid}")
        character_ids.add(c["characterId"])
        rarity = c.get("rarity")
        if rarity not in (3, 4, 5):
            raise ValidationError(f"Unsupported rarity on {cid}: {rarity}")
        if rarity == 5:
            five += 1
        max_level = c.get("maxLevel")
        if not isinstance(max_level, int) or max_level <= 0:
            raise ValidationError(f"Invalid maxLevel on {cid}")
        if not isinstance(c.get("levelBaseValues"), list) or len(c["levelBaseValues"]) != max_level:
            raise ValidationError(f"Invalid level curve on {cid}")
        if not isinstance(c.get("bloomStages"), list) or len(c["bloomStages"]) != 6:
            raise ValidationError(f"Invalid Bloom profile on {cid}")
        for field in ("activeLevels", "passiveLevels", "specialLevels"):
            levels = c.get(field)
            if not isinstance(levels, dict) or "1" not in levels or "2" not in levels:
                raise ValidationError(f"Missing Lv1/Lv2 {field} on {cid}")
        if not isinstance(c.get("outfit"), dict):
            raise ValidationError(f"Invalid Outfit on {cid}")
        if c.get("assetId") is not None and not isinstance(c.get("assetId"), str):
            raise ValidationError(f"Invalid assetId on {cid}")

    if five < min_five_star:
        raise ValidationError("Normalized snapshot has too few 5-star cards")

    expected_counts = Counter(f"{c['rarity']}★" for c in cards)
    if dict(expected_counts) != master.get("counts"):
        raise ValidationError(f"Rarity counts do not match cards: {dict(expected_counts)} vs {master.get('counts')}")

    return master


def semantic_diff(a: Any, b: Any, *, ignore_paths: set[tuple[str, ...]] | None = None):
    """Return a compact recursive semantic diff useful for regression diagnostics."""
    ignore_paths = ignore_paths or set()
    diffs = []

    def walk(x, y, path=()):
        if path in ignore_paths:
            return
        if isinstance(x, (int, float)) and not isinstance(x, bool) and isinstance(y, (int, float)) and not isinstance(y, bool):
            if abs(float(x) - float(y)) > 1e-12:
                diffs.append((path, x, y))
            return
        if type(x) is not type(y):
            diffs.append((path, x, y)); return
        if isinstance(x, dict):
            keys = set(x) | set(y)
            for k in sorted(keys):
                if k not in x or k not in y:
                    diffs.append((path + (str(k),), x.get(k, "<missing>"), y.get(k, "<missing>")))
                else:
                    walk(x[k], y[k], path + (str(k),))
        elif isinstance(x, list):
            if len(x) != len(y):
                diffs.append((path + ("length",), len(x), len(y)))
            for i, (xx, yy) in enumerate(zip(x, y)):
                walk(xx, yy, path + (str(i),))
        elif x != y:
            diffs.append((path, x, y))

    walk(a, b)
    return diffs
