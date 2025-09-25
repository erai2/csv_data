import os, json

def parse_documents(folder="docs"):
    parsed = {}
    for fname in os.listdir(folder):
        if not fname.endswith((".md", ".txt", ".csv")):
            continue
        with open(os.path.join(folder, fname), encoding="utf-8") as f:
            text = f.read()

        paragraphs = []
        for i, block in enumerate(text.split("\n\n"), start=1):
            block = block.strip()
            if not block:
                continue
            category = "rule" if any(k in block for k in ["合", "沖", "刑", "破", "穿", "묘고", "대상"]) else "concept"
            rule_type = None
            if "合" in block: rule_type = "합"
            elif "沖" in block: rule_type = "충"
            elif "刑" in block: rule_type = "형"
            elif "破" in block: rule_type = "파"
            elif "穿" in block: rule_type = "천"
            elif "묘고" in block: rule_type = "묘고"
            elif "대상" in block: rule_type = "대상"

            paragraphs.append({
                "id": f"{fname}_{i}",
                "category": category,
                "rule_type": rule_type,
                "content": block
            })

        parsed[fname] = {"paragraphs": paragraphs}

    os.makedirs("parsed", exist_ok=True)
    with open("parsed/parsed_keywords.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    return parsed

if __name__ == "__main__":
    result = parse_documents("docs")
    print("✅ 파싱 완료 → parsed/parsed_keywords.json")
