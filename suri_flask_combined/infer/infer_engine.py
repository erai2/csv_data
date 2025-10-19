
import json

def infer_from_chart(chart, rules):
    interpretation = []

    for rule_id, rule in rules.items():
        for logic in rule.get("logic", []):
            conditions = logic.get("if", [])
            match = all(cond in chart["relations"] or cond in chart["tags"] for cond in conditions)

            if match:
                explanation = logic.get("explanation", {})
                result = explanation.get("default", "")
                if any(r in chart["relations"] for r in rule.get("relations", {}).get("地支破", [])):
                    result += " " + explanation.get("with_破", "")
                if "大運合" in chart.get("tags", []):
                    result += " " + explanation.get("with_大運合", "")
                interpretation.append(f"[{rule_id}] {result.strip()}")
    return interpretation
