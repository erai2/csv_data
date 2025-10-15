def infer_logic(structure):
    relations = [relation[2] for relation in structure.get("감지관계", [])]
    result = []

    if "破" in relations:
        result.append({"카테고리": "혼인", "조건": "破", "결과": "이혼"})
    if "合" in relations:
        result.append({"카테고리": "인연", "조건": "合", "결과": "연애·재결합"})
    if not result:
        result.append({"카테고리": "일반", "조건": "-", "결과": "평온"})

    return result


__all__ = ["infer_logic"]
