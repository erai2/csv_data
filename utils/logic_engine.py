from typing import Dict, List


def infer_logic(structure: Dict[str, List[str]]) -> List[Dict[str, str]]:
    relations = [relation[2] for relation in structure.get("감지관계", [])]
    result: List[Dict[str, str]] = []

    if "破" in relations:
        result.append(
            {
                "카테고리": "혼인",
                "조건": "午卯破",
                "결과": "이혼",
                "설명": "배우자궁 파괴로 인연 단절",
            }
        )
    if "合" in relations:
        result.append(
            {
                "카테고리": "관계",
                "조건": "卯亥合",
                "결과": "연애 또는 재결합",
                "설명": "합으로 인연 재형성",
            }
        )
    if not result:
        result.append(
            {
                "카테고리": "일반",
                "조건": "-",
                "결과": "평온",
                "설명": "특이 작용 없음",
            }
        )

    return result
