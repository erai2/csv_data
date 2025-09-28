import re
from datetime import datetime

def parse_content(text: str, source="uploaded_doc"):
    """
    문서 내용을 concepts / rules / cases 로 정밀 분류
    """
    lines = text.splitlines()
    data = {"concepts": [], "rules": [], "cases": []}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 규칙 (조건 → 결과)
        if "→" in line:
            parts = line.split("→")
            condition = parts[0].strip()
            result = parts[1].strip() if len(parts) > 1 else ""
            relation_type = "합" if "合" in result or "合" in condition else \
                            "충" if "沖" in result else "기타"
            ohaeng = re.findall(r"[金木水火土]", result)
            data["rules"].append({
                "rule_id": f"R{len(data['rules'])+1:03}",
                "condition_text": condition,
                "result_text": result,
                "relation_type": relation_type,
                "ohaeng": ohaeng[0] if ohaeng else "",
                "source": source,
                "created_at": now
            })

        # 사례
        elif "사례" in line or line.startswith("<사례"):
            data["cases"].append({
                "case_id": f"S{len(data['cases'])+1:03}",
                "saju_text": line,
                "relations_found": "",
                "interpretation": "",
                "source": source,
                "created_at": now
            })

        # 개념
        elif "개념" in line or "이론" in line or line.startswith("Part"):
            data["concepts"].append({
                "concept_id": f"C{len(data['concepts'])+1:03}",
                "name": line[:30],
                "definition": line,
                "example": "",
                "related_rules": "",
                "source": source,
                "created_at": now
            })

    return data
