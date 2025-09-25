# universal_parser.py
# parser.py
import os
import json
import re

def split_paragraphs(text):
    """
    문단 단위로 분리 (빈 줄 기준)
    """
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def classify_paragraph(para):
    """
    문단을 rule / case / concept 으로 분류
    - 간단한 키워드 기반 (추후 AI 모델 연동 가능)
    """
    # 규칙 (rules)
    if any(kw in para for kw in ["合", "沖", "刑", "破", "穿", "묘고", "허실", "帶象", "응기", "조건"]):
        return "rule"

    # 사례 (cases)
    if any(kw in para for kw in ["사례", "예시", "사주", "남명", "여명", "일주", "대운", "세운"]):
        return "case"

    # 개념 (concepts)
    if any(kw in para for kw in ["의미", "정의", "설명", "상", "법", "원리", "궁위", "십신", "오행"]):
        return "concept"

    return "unknown"

def parse_document(content):
    """
    문서 → 문단 단위로 추출 + 카테고리 분류
    """
    result = {"paragraphs": []}
    for i, para in enumerate(split_paragraphs(content), 1):
        result["paragraphs"].append({
            "id": i,
            "category": classify_paragraph(para),
            "content": para
        })
    return result

def parse_documents(folder="docs"):
    """
    docs 폴더의 모든 .txt/.md 문서를 JSON으로 변환
    """
    parsed = {}
    for fname in os.listdir(folder):
        if not fname.endswith((".txt", ".md")):
            continue
        with open(os.path.join(folder, fname), encoding="utf-8") as f:
            content = f.read()
        parsed[fname] = parse_document(content)

    with open("parsed_all.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    return parsed

if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    result = parse_documents("docs")
    print("✅ 문단 + 카테고리 파싱 완료 → parsed_all.json")
    print("📂 처리된 파일:", list(result.keys()))
