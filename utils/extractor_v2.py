import os
import re
import zipfile
from typing import Dict, List

import pdfplumber
from docx import Document


RULE_PATTERN = re.compile(r"(.*?)→(.*?)\n")
TERM_PATTERN = re.compile(r"([甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥\w]{1,5})[:：]\s*(.+)")


def _read_text_from_file(path: str) -> str:
    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    if path.endswith(".docx"):
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    if path.endswith(".pdf"):
        text_chunks: List[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
        return "\n".join(text_chunks)
    if path.endswith(".zip"):
        text_chunks = []
        with zipfile.ZipFile(path) as zipped:
            for name in zipped.namelist():
                if name.endswith(".txt"):
                    text_chunks.append(zipped.read(name).decode("utf-8"))
        return "\n".join(text_chunks)
    return ""


def extract_rules_and_terms(path: str) -> Dict[str, List[Dict[str, str]]]:
    text = _read_text_from_file(path)

    rules = [
        {
            "condition": match[0].strip(),
            "result": match[1].strip(),
            "category": "일반",
            "description": "",
            "source": os.path.basename(path),
        }
        for match in RULE_PATTERN.findall(text)
    ]

    terms = [
        {
            "term": match[0].strip(),
            "definition": match[1].strip(),
            "category": "명리용어",
        }
        for match in TERM_PATTERN.findall(text)
    ]

    return {"rules": rules, "terms": terms}
