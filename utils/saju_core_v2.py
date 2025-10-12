"""Core structural analysis utilities for the explainable fortune system."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


def analyze_saju(gan: Sequence[str], zhi: Sequence[str], gender: str) -> Dict[str, Any]:
    """Return a structural summary for the supplied four pillars data."""

    gan_list = _normalise_sequence(gan, HEAVENLY_STEMS)
    zhi_list = _normalise_sequence(zhi, EARTHLY_BRANCHES)
    pairs = [f"{g}{z}" for g, z in zip(gan_list, zhi_list)]

    relations = _derive_relations(zhi_list)
    geokguk = _derive_geokguk(gan_list, zhi_list, relations)
    focus = _derive_focus(relations, geokguk)

    return {
        "성별": gender,
        "천간": gan_list,
        "지지": zhi_list,
        "조합": pairs,
        "격국": geokguk,
        "관계": relations,
        "대상": focus,
    }


def _normalise_sequence(values: Sequence[str], valid: Sequence[str]) -> List[str]:
    """Ensure the list has four canonical entries."""

    prepared = [str(v).strip() for v in values if str(v).strip()]
    while len(prepared) < 4:
        prepared.append(valid[len(prepared) % len(valid)])
    return prepared[:4]


def _derive_relations(zhi_list: Sequence[str]) -> List[str]:
    """Identify common 합/충/형/파 relations within the branches."""

    zhi_set = set(zhi_list)
    relations: List[str] = []

    mapping = {
        frozenset({"午", "卯"}): "午卯破",
        frozenset({"卯", "亥"}): "卯亥合",
        frozenset({"戌", "辰"}): "戌辰沖",
        frozenset({"子", "午"}): "子午沖",
        frozenset({"丑", "未"}): "丑未沖",
        frozenset({"寅", "申"}): "寅申沖",
        frozenset({"卯", "酉"}): "卯酉沖",
        frozenset({"辰", "酉"}): "辰酉合",
        frozenset({"亥", "寅"}): "亥寅合",
    }

    for combo, label in mapping.items():
        if combo.issubset(zhi_set):
            relations.append(label)

    if "辰" in zhi_set and "戌" not in zhi_set:
        relations.append("財庫開")
    if "戌" in zhi_set and "辰" not in zhi_set:
        relations.append("官庫開")

    # Detect 인성 충/파 사례
    if "印" not in relations:
        if "卯" in zhi_set and "酉" in zhi_set:
            relations.append("印沖")
        elif "卯" in zhi_set and "午" in zhi_set:
            relations.append("印破")

    return relations


def _derive_geokguk(gan_list: Sequence[str], zhi_list: Sequence[str], relations: Sequence[str]) -> str:
    """Approximate the 격국 (structure archetype) from the pillars."""

    if not gan_list:
        return "일반격"

    day_master = gan_list[1] if len(gan_list) > 1 else gan_list[0]
    has_metal = any(g in {"庚", "辛"} for g in gan_list)
    has_water = any(g in {"壬", "癸"} for g in gan_list)
    has_fire = any(g in {"丙", "丁"} for g in gan_list)
    has_earth = any(g in {"戊", "己"} for g in gan_list)

    if day_master in {"戊", "己"} and has_metal and has_water:
        return "官印相生格"
    if day_master in {"丙", "丁"} and has_earth and has_metal:
        return "食神生財格"
    if "卯亥合" in relations and has_fire:
        return "木火通明格"
    if day_master in {"庚", "辛"} and "財庫開" in relations:
        return "財星護身格"
    return "평격"


def _derive_focus(relations: Sequence[str], geokguk: str) -> List[str]:
    """Highlight notable focuses derived from relations and structure."""

    focus: List[str] = []
    if any("財" in rel for rel in relations):
        focus.append("財統官")
    if any(tag in relations for tag in ["印破", "印沖"]):
        focus.append("印護身")
    if "官印相生格" in geokguk:
        focus.append("官印相生")
    if "食神生財格" in geokguk:
        focus.append("食神生財")
    return focus

