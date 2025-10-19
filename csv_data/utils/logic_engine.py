from typing import Any, Dict, List

RELATION_TO_RESULT = {
    "破": {"카테고리": "혼인", "결과": "이혼"},
    "合": {"카테고리": "인연", "결과": "연애·재결합"}
}

DEFAULT_RESULT = {"카테고리": "일반", "조건": "-", "결과": "평온"}

def infer_logic(structure: Dict[str, Any]) -> List[Dict[str, str]]:
    relations = [rel[2] for rel in structure.get("감지관계", [])]
    result = []

    for relation in relations:
        if relation in RELATION_TO_RESULT:
            outcome = RELATION_TO_RESULT[relation].copy()
            outcome["조건"] = relation
            result.append(outcome)

    return result if result else [DEFAULT_RESULT]

__all__ = ["infer_logic"]
