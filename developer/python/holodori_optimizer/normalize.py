from __future__ import annotations

from collections import defaultdict
import re
from typing import Any

from .constants import ATTRIBUTE_LABELS, ATTRIBUTE_MARKUP, SOURCE_NAME


class NormalizationError(RuntimeError):
    pass


_MARKUP_RE = re.compile(r"\[/?(?:highlight|attribute(?:=[^\]]+)?)\]")
_SELF_TRIGGER_RE = re.compile(r"^With\s+(\d+)\s+or more\s+(.+?)\s+Members,", re.I)
_ATTRIBUTE_MARKUP_RE = re.compile(r"\[attribute=([^\]]+)\]", re.I)
_RARITY_RE = re.compile(r"_RARITY_(\d+)$")


def strip_markup(value: Any) -> str:
    text = _MARKUP_RE.sub("", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def data_rows(raw: dict[str, list], name: str) -> list[dict]:
    arr = raw.get(name)
    if not isinstance(arr, list):
        raise NormalizationError(f"{name} is missing or is not an array")
    return [x.get("data") for x in arr if isinstance(x, dict) and x.get("data")]


def id_map(raw: dict[str, list], name: str) -> dict[str, dict]:
    return {x["id"]: x for x in data_rows(raw, name)}


def lang_map(raw: dict[str, list], name: str) -> dict[str, str]:
    return {x["id"]: x.get("text", "") for x in data_rows(raw, name)}


def group_map_rows(rows: list[dict], key: str) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = defaultdict(dict)
    for x in rows:
        out[x[key]][int(x["level"])] = x
    return dict(out)


def group_list_rows(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for x in rows:
        out[x[key]].append(x)
    return dict(out)


def rarity_int(value: Any) -> int | None:
    m = _RARITY_RE.search(str(value or ""))
    return int(m.group(1)) if m else None


def _number(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def normalize_master(raw: dict[str, list], source_version: str) -> dict:
    cards = data_rows(raw, "Card.json")
    chars = id_map(raw, "Character.json")
    groups = id_map(raw, "CharacterGrouping.json")
    lang_card = lang_map(raw, "LangCard_Eng.json")
    lang_group = lang_map(raw, "LangCharacterGrouping_Eng.json")
    lang_passive = lang_map(raw, "LangGeneratedLivePassiveSkillLevel_Eng.json")
    lang_active = lang_map(raw, "LangGeneratedLiveActiveSkillLevel_Eng.json")
    lang_special = lang_map(raw, "LangGeneratedLiveSpecialSkillLevel_Eng.json")
    lang_leader = lang_map(raw, "LangGeneratedLiveLeaderSkill_Eng.json")

    group_labels = {gid: lang_group.get(g.get("nameLangId"), gid) for gid, g in groups.items()}

    char_group_ids: dict[str, list[str]] = {cid: [] for cid in chars}
    for gid, group in groups.items():
        for cid in group.get("characterIds") or []:
            char_group_ids.setdefault(cid, []).append(gid)
    for cid, ch in chars.items():
        arr = char_group_ids.setdefault(cid, [])
        for gid in ch.get("regularCharacterGroupingIds") or []:
            if gid not in arr:
                arr.append(gid)

    level_by_group: dict[str, dict[int, int]] = defaultdict(dict)
    for x in data_rows(raw, "CardLevel.json"):
        level_by_group[x["groupId"]][int(x["level"])] = int(x["parameterBaseValue"])

    limit_by_group: dict[str, list[int]] = defaultdict(list)
    for x in data_rows(raw, "CardLevelLimit.json"):
        limit_by_group[x["groupId"]].append(int(x["levelLimit"]))
    for arr in limit_by_group.values():
        arr.sort()

    potential_by_group = group_list_rows(data_rows(raw, "CardPotential.json"), "groupId")
    for arr in potential_by_group.values():
        arr.sort(key=lambda x: int(x["upgradeCount"]))

    active_levels = group_map_rows(data_rows(raw, "LiveActiveSkillLevel.json"), "liveActiveSkillId")
    passive_levels = group_map_rows(data_rows(raw, "LivePassiveSkillLevel.json"), "livePassiveSkillId")
    special_levels = group_map_rows(data_rows(raw, "LiveSpecialSkillLevel.json"), "liveSpecialSkillId")

    active_effect = {x["groupId"]: x for x in data_rows(raw, "LiveActiveSkillEffect.json")}
    passive_effect = {x["groupId"]: x for x in data_rows(raw, "LivePassiveSkillEffect.json")}
    targets = id_map(raw, "LiveSkillEffectTarget.json")
    trigger_rows = {x["groupId"]: x for x in data_rows(raw, "LiveSkillTrigger.json")}
    leaders = id_map(raw, "LiveLeaderSkill.json")

    group_by_label = {str(label).lower(): gid for gid, label in group_labels.items()}

    def normalize_trigger(t: dict | None):
        if not t:
            return None
        typ = t.get("type") or ""
        if typ.endswith("DECK_CARD_ATTRIBUTE"):
            return {"kind": "attribute", "id": t.get("cardAttributeType"), "count": int(t.get("threshold") or 1)}
        if typ.endswith("DECK_CARD_CHARACTER_GROUPING"):
            return {"kind": "group", "id": t.get("characterGroupingId"), "count": int(t.get("threshold") or 1)}
        if typ.endswith("COMBO_GTE"):
            return {"kind": "combo_gte", "threshold": int(t.get("threshold") or 0)}
        if typ.endswith("LIFE_GTE"):
            return {"kind": "life_gte", "threshold": int(t.get("threshold") or 0)}
        if typ.endswith("LIFE_LTE"):
            return {"kind": "life_lte", "threshold": int(t.get("threshold") or 0)}
        if typ.endswith("JUDGEMENT_TYPE_GTE"):
            return {"kind": "judgement_gte", "threshold": int(t.get("threshold") or 0), "judgement": t.get("liveNoteJudgementType")}
        return {
            "kind": "unsupported",
            "type": typ,
            "threshold": t.get("threshold"),
            "groupId": t.get("characterGroupingId"),
            "attributeId": t.get("cardAttributeType"),
        }

    def normalize_target(t: dict | None):
        if not t:
            return {"kind": "unsupported", "type": "missing"}
        typ = t.get("type") or ""
        if typ.endswith("_ALL"):
            return {"kind": "all"}
        if typ.endswith("_SELF"):
            return {"kind": "self"}
        if typ.endswith("_ATTRIBUTE"):
            return {"kind": "attribute", "id": t.get("cardAttributeType"), "count": int(t.get("targetCount") or 1)}
        if typ.endswith("_CHARACTER_GROUPING"):
            return {"kind": "group", "id": t.get("characterGroupingId"), "count": int(t.get("targetCount") or 0)}
        return {"kind": "unsupported", "type": typ}

    def parse_self_trigger(text: str):
        m = _SELF_TRIGGER_RE.match(str(text or ""))
        if not m:
            raise NormalizationError(f"Cannot parse self-passive trigger: {text}")
        count = int(m.group(1))
        raw_label = m.group(2)
        am = _ATTRIBUTE_MARKUP_RE.search(raw_label)
        if am:
            attr_id = ATTRIBUTE_MARKUP.get(am.group(1).lower())
            if not attr_id:
                raise NormalizationError(f"Unknown passive attribute {am.group(1)} in: {text}")
            return {"kind": "attribute", "id": attr_id, "count": count}
        label = strip_markup(raw_label)
        gid = group_by_label.get(label.lower())
        if not gid:
            raise NormalizationError(f"Unknown passive group {label} in: {text}")
        return {"kind": "group", "id": gid, "count": count}

    def passive_kind(typ: str) -> str:
        if typ.endswith("PERFORMANCE_UP_PERMIL_UP"):
            return "perf"
        if typ.endswith("TECHNIQUE_UP_PERMIL_UP"):
            return "tech"
        if typ.endswith("SENSE_UP_PERMIL_UP"):
            return "sense"
        if typ.endswith("ALL_PARAMETER_UP_PERMIL_UP"):
            return "all"
        if typ.endswith("LIVE_ACTIVE_SKILL_EFFECT_UP_PERMIL_UP"):
            return "support"
        return "unsupported"

    def score_value(effect: dict | None):
        if not effect:
            return None
        typ = effect.get("type") or ""
        if typ.endswith("SCORE_UP_PERMIL_UP") or typ.endswith("SCORE_UP_EFFECT_UP_PERMIL_UP"):
            return _number(effect.get("value")) / 10
        return None

    def sar_value(effect: dict | None):
        if effect and (effect.get("type") or "").endswith("LIVE_ACTIVE_SKILL_ACTIVATION_PROBABILITY_UP_PERMIL_UP"):
            return _number(effect.get("value")) / 1000
        return 0.0

    def active_level(x: dict):
        base = active_effect.get(x.get("liveActiveSkillEffectGroupId"))
        base_magnitude = score_value(base)
        if base_magnitude is None:
            raise NormalizationError(f"Unsupported card Active primary effect {base and base.get('type')}")
        conditional_magnitude = None
        trigger = None
        if x.get("additionalLiveActiveSkillEffectGroupId"):
            effect = active_effect.get(x["additionalLiveActiveSkillEffectGroupId"])
            conditional_magnitude = score_value(effect)
            if conditional_magnitude is None:
                raise NormalizationError(f"Unsupported card Active additional effect {effect and effect.get('type')}")
            trigger = normalize_trigger(trigger_rows.get(x.get("additionalLiveSkillTriggerGroupId")))
        probability = _number(x.get("activationProbabilityPermilMultiply")) / 1000
        if abs(probability - 0.55) < 1e-9:
            chance_label = "H"
        elif abs(probability - 0.46) < 1e-9:
            chance_label = "M"
        elif abs(probability - 0.37) < 1e-9:
            chance_label = "L"
        else:
            chance_label = f"{probability * 100:.1f}%"
        return {
            "level": int(x["level"]),
            "baseMagnitude": base_magnitude,
            "conditionalMagnitude": conditional_magnitude,
            "trigger": trigger,
            "duration": _number(x.get("effectDurationMillisecond")) / 1000,
            "interval": _number(x.get("coolTimeMillisecond")) / 1000,
            "probability": probability,
            "chanceLabel": chance_label,
            "text": strip_markup(lang_active.get(x.get("descriptionLangId"), "")),
        }

    def passive_level(x: dict):
        effect = passive_effect.get(x.get("livePassiveSkillEffectGroupId"))
        if not effect:
            raise NormalizationError(f"Missing passive effect {x.get('livePassiveSkillEffectGroupId')}")
        target = normalize_target(targets.get(effect.get("liveSkillEffectTargetId")))
        kind = passive_kind(effect.get("type") or "")
        if kind == "unsupported":
            raise NormalizationError(f"Unsupported card Passive effect {effect.get('type')}")
        text = lang_passive.get(x.get("descriptionLangId"), "")
        trigger = None
        if target["kind"] == "self":
            trigger = parse_self_trigger(text)
        elif target["kind"] in ("attribute", "group"):
            trigger = {"kind": target["kind"], "id": target.get("id"), "count": target.get("count") or 1}
        return {
            "level": int(x["level"]),
            "kind": kind,
            "pct": _number(effect.get("value")) / 1000,
            "target": target,
            "trigger": trigger,
            "text": strip_markup(text),
        }

    def special_level(x: dict):
        base = active_effect.get(x.get("liveActiveSkillEffectGroupId"))
        magnitude = score_value(base)
        if magnitude is None:
            raise NormalizationError(f"Unsupported card Special primary effect {base and base.get('type')}")
        sar_pct = 0
        sar_trigger = None
        unsupported = []
        if x.get("additionalLiveActiveSkillEffectGroupId"):
            effect = active_effect.get(x["additionalLiveActiveSkillEffectGroupId"])
            sar_pct = sar_value(effect)
            if sar_pct:
                sar_trigger = normalize_trigger(trigger_rows.get(x.get("additionalLiveSkillTriggerGroupId")))
            elif effect:
                unsupported.append({"type": effect.get("type"), "value": effect.get("value")})
        return {
            "level": int(x["level"]),
            "magnitude": magnitude,
            "duration": _number(x.get("effectDurationMillisecond")) / 1000,
            "sarPct": sar_pct,
            "sarTrigger": sar_trigger,
            "unsupported": unsupported,
            "text": strip_markup(lang_special.get(x.get("descriptionLangId"), "")),
        }

    def normalize_leader(card_id: str):
        leader = leaders.get(f"live_leader_skill-{card_id}")
        if not leader:
            raise NormalizationError(f"Missing Leader/Outfit for {card_id}")
        effects = []
        for effect_field, trigger_field in (
            ("livePassiveSkillEffectGroupId", "liveSkillTriggerGroupId"),
            ("additionalLivePassiveSkillEffectGroupId", "additionalLiveSkillTriggerGroupId"),
        ):
            gid = leader.get(effect_field)
            if not gid:
                continue
            effect = passive_effect.get(gid)
            if not effect:
                raise NormalizationError(f"Missing Leader effect {gid}")
            kind = passive_kind(effect.get("type") or "")
            target = normalize_target(targets.get(effect.get("liveSkillEffectTargetId")))
            if kind == "unsupported" or target.get("kind") != "all":
                raise NormalizationError(f"Unsupported Leader effect {effect.get('type')} / {target.get('kind')}")
            effects.append({
                "kind": kind,
                "pct": _number(effect.get("value")) / 1000,
                "trigger": normalize_trigger(trigger_rows.get(leader.get(trigger_field))),
            })
        return {
            "effects": effects,
            "text": strip_markup(lang_leader.get(leader.get("descriptionLangId"), "")),
        }

    def bloom_stages(group_id: str):
        arr = potential_by_group.get(group_id)
        if not arr or len(arr) != 5:
            raise NormalizationError(f"Expected five Bloom rows for {group_id}")
        by_stage = {int(x["upgradeCount"]): x for x in arr}
        stat_bonus = 0
        active_level_no = 1
        passive_level_no = 1
        special_level_no = 1
        connect_level = 1
        out = [{"stage": 0, "statBonus": 0, "activeLevel": 1, "passiveLevel": 1, "specialLevel": 1, "connectLevel": 1}]
        for stage in range(1, 6):
            x = by_stage.get(stage)
            if not x:
                raise NormalizationError(f"Missing Bloom stage {stage} for {group_id}")
            typ = x.get("effectType") or ""
            value = _number(x.get("value"))
            if typ.endswith("ALL_PARAMETER_UP_PERMIL_UP"):
                stat_bonus += value / 1000
            elif typ.endswith("ACTIVE_SKILL_LEVEL_UP"):
                active_level_no = int(value)
            elif typ.endswith("PASSIVE_SKILL_LEVEL_UP"):
                passive_level_no = int(value)
            elif typ.endswith("SPECIAL_SKILL_LEVEL_UP"):
                special_level_no = int(value)
            elif typ.endswith("SKILL_TREE_CONNECT_EFFECT_LEVEL_UP"):
                connect_level = int(value)
            else:
                raise NormalizationError(f"Unknown Bloom effect {typ}")
            out.append({
                "stage": stage,
                "statBonus": stat_bonus,
                "activeLevel": active_level_no,
                "passiveLevel": passive_level_no,
                "specialLevel": special_level_no,
                "connectLevel": connect_level,
            })
        return out

    normalized = []
    for c in cards:
        ch = chars.get(c.get("characterId"))
        if not ch:
            raise NormalizationError(f"Missing character {c.get('characterId')}")
        rarity = rarity_int(c.get("rarity"))
        level_map = level_by_group.get(c.get("cardLevelGroupId"))
        if not level_map:
            raise NormalizationError(f"Missing CardLevel group {c.get('cardLevelGroupId')}")
        max_level = max(level_map)
        level_base_values = []
        for level in range(1, max_level + 1):
            if level not in level_map:
                raise NormalizationError(f"Missing {c.get('cardLevelGroupId')} level {level}")
            level_base_values.append(level_map[level])

        al = active_levels.get(c.get("liveActiveSkillId"))
        pl = passive_levels.get(c.get("livePassiveSkillId"))
        sl = special_levels.get(c.get("liveSpecialSkillId"))
        if not al or 1 not in al or 2 not in al or not pl or 1 not in pl or 2 not in pl or not sl or 1 not in sl or 2 not in sl:
            raise NormalizationError(f"Missing Lv1/Lv2 skill data for {c.get('id')}")

        gids = sorted(char_group_ids.get(c.get("characterId"), []))
        name = lang_card.get(c.get("nameLangId"), c.get("id"))
        normalized.append({
            "id": c.get("id"),
            "assetId": c.get("assetId"),  # v2.2: retained for future image resolution.
            "characterId": c.get("characterId"),
            "member": ch.get("nameEng"),
            "name": name,
            "key": f"{ch.get('nameEng')} | {name}",
            "rarity": rarity,
            "attributeId": c.get("attributeType"),
            "attribute": ATTRIBUTE_LABELS.get(c.get("attributeType"), c.get("attributeType")),
            "groupIds": gids,
            "groupLabels": [group_labels.get(g, g) for g in gids],
            "maxLevel": max_level,
            "levelBaseValues": level_base_values,
            "statPermil": [int(c.get("performancePermilMultiply")), int(c.get("techniquePermilMultiply")), int(c.get("sensePermilMultiply"))],
            "levelLimitCaps": list(limit_by_group.get(c.get("cardLevelLimitGroupId"), [])),
            "bloomStages": bloom_stages(c.get("cardPotentialGroupId")),
            "activeLevels": {"1": active_level(al[1]), "2": active_level(al[2])},
            "passiveLevels": {"1": passive_level(pl[1]), "2": passive_level(pl[2])},
            "specialLevels": {"1": special_level(sl[1]), "2": special_level(sl[2])},
            "outfit": normalize_leader(c.get("id")),
        })

    counts: dict[str, int] = {}
    for c in normalized:
        key = f"{c['rarity']}★"
        counts[key] = counts.get(key, 0) + 1

    return {
        "schemaVersion": 2,
        "source": SOURCE_NAME,
        "sourceVersion": str(source_version or "unknown").strip(),
        "cards": normalized,
        "groupLabels": group_labels,
        "attributeLabels": dict(ATTRIBUTE_LABELS),
        "counts": counts,
    }
