import re
from datetime import datetime

def parse_content(text: str, source="uploaded_doc"):
    """
    '소제목 + 설명 문단' 구조를 우선적으로 파싱하여 개념을 추출하고,
    다양한 형식의 문서에 더 유연하게 대응합니다.
    """
    data = {"concepts": [], "rules": [], "cases": []}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saju_pattern = re.compile(r'^[가-힣]{2}\s?[가-힣]{2}\s?[가-힣]{2}\s?[가-힣]{2}\s?\(?[乾坤]\)?')
    
    paragraphs = re.split(r'\n\s*\n', text.strip())

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        
        first_line = lines[0]

        # 1. 사례(Case) 문단 확인 (기존 로직 유지)
        is_case = False
        saju_text, interpretation = "", ""
        if paragraph.startswith('<사례>'):
            if len(lines) > 2:
                saju_text, interpretation = lines[1], "\n".join(lines[2:])
                is_case = True
        elif saju_pattern.match(first_line):
            saju_text, interpretation = first_line, "\n".join(lines[1:])
            is_case = True

        if is_case:
            data["cases"].append({
                "case_id": f"S{len(data['cases'])+1:03}", "saju_text": saju_text,
                "interpretation": interpretation, "relations_found": "", "source": source, "created_at": now
            })
            continue

        # 2. '소제목 + 설명 문단' 형태의 개념(Concept)인지 확인 (핵심 개선 사항)
        # - 문단이 두 줄 이상이고,
        # - 첫 줄(소제목)의 길이가 30자 미만이며,
        # - 첫 줄에 규칙 기호(→)가 없는 경우 -> 개념으로 판단
        if len(lines) > 1 and len(first_line) < 30 and "→" not in first_line:
            concept_name = first_line.replace(':', '').strip()
            concept_def = "\n".join(lines[1:])
            data["concepts"].append({
                "concept_id": f"C{len(data['concepts'])+1:03}", "name": concept_name,
                "definition": concept_def, "example": "", "related_rules": "", "source": source, "created_at": now
            })
            continue

        # 3. 위 조건에 맞지 않는 경우, 문단 내 각 줄을 개별적으로 확인 (기존 방식 보완)
        for line in lines:
            # 규칙(Rule) 확인
            if "→" in line:
                parts = line.split("→")
                condition = parts[0].strip()
                result = parts[1].strip() if len(parts) > 1 else ""
                data["rules"].append({
                    "rule_id": f"R{len(data['rules'])+1:03}", "condition_text": condition,
                    "result_text": result, "relation_type": "규칙", "ohaeng": "".join(re.findall(r"[金木水火土]", line)),
                    "source": source, "created_at": now
                })

            # 한 줄짜리 개념(Concept) 확인
            elif re.match(r'^([가-힣\d\(\)]+)\s*[:：-]\s*(.+)', line):
                match = re.match(r'^([가-힣\d\(\)]+)\s*[:：-]\s*(.+)', line)
                if match:
                    name, definition = match.groups()
                    data["concepts"].append({
                        "concept_id": f"C{len(data['concepts'])+1:03}", "name": name.strip(),
                        "definition": definition.strip(), "example": "", "related_rules": "", "source": source, "created_at": now
                    })

    return data