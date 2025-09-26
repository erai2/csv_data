# parser.py
import re

def parse_content(content: str):
    """문서에서 규칙/개념/사례 문단 전체를 추출"""
    parsed = {"rules": []}

    # 패턴 정의 (필요시 추가 가능)
    patterns = {
        "합": r".*합.*",
        "충": r".*충.*",
        "형": r".*형.*",
        "파": r".*파.*",
        "천": r".*천.*",
        "묘고": r".*묘고.*",
        "대상": r".*대상.*"
    }

    # 문단 단위로 분리
    paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

    for p in paragraphs:
        for cat, pat in patterns.items():
            if re.search(pat, p):
                parsed["rules"].append({
                    "category": cat,
                    "title": f"{cat} 관련 규칙",
                    "content": p
                })
                break
        else:
            # 매칭 안 된 문단도 "기타"로 저장
            parsed["rules"].append({
                "category": "기타",
                "title": p[:20],
                "content": p
            })

    return parsed
