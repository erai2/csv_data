import re
import zipfile

import pdfplumber
from docx import Document


def _read_text(path: str) -> str:
    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    if path.endswith(".docx"):
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if path.endswith(".zip"):
        content = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith(".txt"):
                    content.append(archive.read(name).decode("utf-8"))
        return "\n".join(content)
    return ""


def extract_rules_terms_cases(path: str) -> dict:
    text = _read_text(path)

    rules = [
        {
            "condition": match[0].strip(),
            "result": match[1].strip(),
            "category": "자동추출",
        }
        for match in re.findall(r"([^\n]+?)→([^\n]+)", text)
    ]

    terms = [
        {
            "term": term_match[0].strip(),
            "definition": term_match[1].strip(),
            "category": "용어",
        }
        for term_match in re.findall(
            r"([比劫財官印傷食祿原神墓庫帶象合沖破刑穿\w]{1,4})[:：]\s*([^\n]+)",
            text,
        )
    ]

    case_pattern = (
        r"<사례\s*\d+>[:：]?\s*([^\n]+)\n"
        r"([\w()坤乾⺒卯午未申酉戌亥子丑寅辰巳\s]+)\n"
        r"([\s\S]*?)(?=\n<사례|\Z)"
    )
    cases = []
    for title, chart, content in re.findall(case_pattern, text):
        cleaned_content = content.strip()
        summary_tokens = cleaned_content.split()
        summary = " ".join(summary_tokens[:40]) + ("..." if summary_tokens else "")

        tags = []
        if any(keyword in cleaned_content for keyword in ["破", "合", "沖"]):
            tags.append("혼인")
        if any(keyword in cleaned_content for keyword in ["傷官", "官印"]):
            tags.append("직업")
        if "財" in cleaned_content:
            tags.append("재물")
        if "印" in cleaned_content:
            tags.append("건강")
        if not tags:
            tags.append("기타")

        cases.append(
            {
                "title": title.strip(),
                "chart": chart.strip(),
                "summary": summary if summary else cleaned_content[:120],
                "content": cleaned_content,
                "tags": tags,
            }
        )

    return {"rules": rules, "terms": terms, "cases": cases}


__all__ = ["extract_rules_terms_cases"]
