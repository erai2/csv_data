# parser.py
import re
import json

def parse_content(content: str):
    """문서 내용에서 규칙/사례/용어 등 단순 패턴 기반 추출"""
    rules = []

    # 예시 패턴: "…의 상", "…법", "…원리", "…의미"
    for match in re.finditer(r"([^\s]+의\s?(상|법|원리|의미))", content):
        title = match.group(1)
        rules.append({
            "category": "rule",
            "title": title,
            "content": content[max(0, match.start()-50):match.end()+100]  # 앞뒤 문맥 포함
        })

    return {"rules": rules}

def save_parsed(data, filename="parsed_all.json"):
    """저장 버튼 눌렀을 때만 실행"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
