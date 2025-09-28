import re
from datetime import datetime

def parse_content(text: str, source="uploaded_doc"):
    lines = text.splitlines()
    data = {"concepts": [], "rules": [], "cases": []}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for line in lines:
        line = line.strip()
        if not line: 
            continue

        # 개념 (용어 정의)
        if any(kw in line for kw in ["궁위", "십신", "대상", "묘고", "록", "역마", "공망", "겁살"]):
            data["concepts"].append({
                "concept_id": f"C{len(data['concepts'])+1:03}",
                "name": line.split()[0],
                "definition": line,
                "example": "",
                "related_rules": "",
                "source": source,
                "created_at": now
            })

        # 규칙 (조건 → 결과)
        elif "→" in line or any(kw in line for kw in ["허투","합","충","형","파","입묘","제압","格"]):
            parts = re.split(r"→|=", line)
            condition = parts[0].strip()
            result = parts[1].strip() if len(parts) > 1 else ""
            data["rules"].append({
                "rule_id": f"R{len(data['rules'])+1:03}",
                "condition_text": condition,
                "result_text": result,
                "relation_type": "규칙",
                "ohaeng": "".join(re.findall(r"[金木水火土]", line)),
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

    return data
