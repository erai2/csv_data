import json
import os

def load_rules():
    with open("rules/rules_master.json", "r", encoding="utf-8") as f:
        return json.load(f)

def match_rules(chart):
    """
    chart = {
      "day_stem": "辛",
      "branches": ["巳","午","卯","亥"],
      "relations": ["午卯破","丑午穿"]
    }
    """
    rules = load_rules()
    matched = {}

    for rule_id, rule in rules.items():
        text = json.dumps(rule, ensure_ascii=False)
        cond_day = chart["day_stem"] in text
        cond_branch = any(b in text for b in chart["branches"])
        cond_relation = any(r in text for r in chart["relations"])
        matched[rule_id] = cond_day or cond_branch or cond_relation

    return matched
