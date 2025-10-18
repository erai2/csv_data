import json
import re
import zipfile
from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import pandas as pd
import pdfplumber
from docx import Document


def _read_text(path: str) -> str:
    """Load textual content from a variety of supported document formats."""

    suffix = Path(path).suffix.lower()

    if suffix in {".txt", ".md"}:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    if suffix == ".docx":
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    if suffix == ".pdf":
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if suffix in {".xlsx", ".xls"}:
        try:
            sheets = pd.read_excel(path, sheet_name=None, dtype=str)
        except ValueError:
            sheets = pd.read_excel(path, sheet_name=None)
        content: List[str] = []
        for sheet_name, frame in sheets.items():
            content.append(f"[시트: {sheet_name}]")
            text_values = frame.fillna("").astype(str).values.ravel()
            content.append("\n".join(value for value in text_values if value.strip()))
        return "\n".join(content)

    if suffix == ".zip":
        content = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                inner_suffix = Path(name).suffix.lower()
                if inner_suffix in {".txt", ".md"}:
                    content.append(archive.read(name).decode("utf-8"))
        return "\n".join(content)

    return ""


def _load_structured_json(path: str) -> Dict[str, Iterable]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict) and {"rules", "terms", "cases"} & data.keys():
        rules = list(data.get("rules", []))
        terms = list(data.get("terms", []))
        cases = list(data.get("cases", []))
        return {
            "rules": rules if isinstance(rules, list) else [],
            "terms": terms if isinstance(terms, list) else [],
            "cases": cases if isinstance(cases, list) else [],
        }

    text_parts: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            text_parts.append(f"{key}: {value}")
    elif isinstance(data, list):
        text_parts.extend(str(item) for item in data)

    return {"text": "\n".join(text_parts)}


def _extract_rules_from_text(text: str) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []

    for condition, result in re.findall(r"([^\n]+?)→([^\n]+)", text):
        rules.append(
            {
                "condition": condition.strip(),
                "result": result.strip(),
                "category": "자동추출",
            }
        )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or "→" in stripped:
            continue

        if any(keyword in stripped for keyword in ["이다", "의 작용", "작용은", "작용을"]):
            subject = stripped
            if "의 작용" in stripped:
                subject = stripped.split("의 작용", 1)[0].strip()
            elif "작용은" in stripped:
                subject = stripped.split("작용은", 1)[0].strip()
            elif "이다" in stripped:
                subject = stripped.split("이다", 1)[0].strip()

            rules.append(
                {
                    "condition": subject,
                    "result": stripped,
                    "category": "자연어",
                }
            )

    return rules


def _extract_terms_from_text(text: str) -> List[Dict[str, Any]]:
    terms: List[Dict[str, Any]] = []

    for term, definition in re.findall(
        r"([比劫財官印傷食祿原神墓庫帶象合沖破刑穿\w]{1,6})[:：]\s*([^\n]+)",
        text,
    ):
        terms.append(
            {
                "term": term.strip(),
                "definition": definition.strip(),
                "category": "용어",
            }
        )

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or any(marker in stripped for marker in [":", "："]):
            continue

        if "이라 한다" in stripped or "의 의미는" in stripped:
            if "이라 한다" in stripped:
                term_part, definition_part = stripped.split("이라 한다", 1)
            else:
                term_part, definition_part = stripped.split("의 의미는", 1)

            term = term_part.strip().rstrip("는은이")
            definition = definition_part.strip().lstrip("는은이").strip()

            if term:
                terms.append(
                    {
                        "term": term,
                        "definition": definition or stripped,
                        "category": "자연어",
                    }
                )

    return terms


def _collect_case_block(lines: Sequence[str], start_index: int) -> Dict[str, Any]:
    header = lines[start_index].strip()
    match = re.match(r"(예|사례|명조)[\s\d#-]*[:：]\s*(.*)", header)
    title = match.group(2).strip() if match and match.group(2).strip() else header

    content_lines: List[str] = []
    index = start_index + 1
    while index < len(lines) and lines[index].strip():
        content_lines.append(lines[index])
        index += 1

    return {
        "title": title,
        "content_lines": content_lines,
        "next_index": index,
    }


def _extract_cases_from_text(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    cases: List[Dict[str, Any]] = []
    index = 0
    counter = 1

    trigger_pattern = re.compile(r"^(예|사례|명조)[\s\d#-]*[:：]")

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue

        if trigger_pattern.match(line):
            block = _collect_case_block(lines, index)
            content = "\n".join(block["content_lines"]).strip()
            title = block["title"] or f"사례 {counter}"
            summary = content.split("\n", 1)[0][:120] if content else ""

            cases.append(
                {
                    "title": title,
                    "chart": "",
                    "summary": summary or title,
                    "content": content or title,
                    "tags": [],
                }
            )

            index = block["next_index"] + 1
            counter += 1
        else:
            index += 1

    return cases


def _annotate_links(
    rules: List[Dict[str, Any]],
    terms: List[Dict[str, Any]],
    cases: List[Dict[str, Any]],
) -> None:
    term_names = [term.get("term", "") for term in terms]

    for rule in rules:
        text = " ".join(filter(None, [rule.get("condition"), rule.get("result")]))
        linked_terms = [name for name in term_names if name and name in text]
        if linked_terms:
            rule["linked_terms"] = linked_terms

    rule_titles = [rule.get("condition", "") for rule in rules]

    for term in terms:
        definition_text = term.get("definition", "")
        linked_rules = [title for title in rule_titles if title and title in definition_text]
        if linked_rules:
            term["linked_rules"] = linked_rules

    for case in cases:
        content_text = case.get("content", "")
        linked_terms = [name for name in term_names if name and name in content_text]
        if linked_terms:
            case["linked_terms"] = linked_terms

        linked_rules = [title for title in rule_titles if title and title in content_text]
        if linked_rules:
            case["linked_rules"] = linked_rules


def _ensure_defaults(payload: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    for key in ("rules", "terms", "cases"):
        if not payload.get(key):
            payload[key] = [
                {
                    "condition": "unknown",
                    "result": "unknown",
                    "category": "unknown",
                }
            ] if key == "rules" else [
                {
                    "term": "unknown",
                    "definition": "unknown",
                    "category": "unknown",
                }
            ] if key == "terms" else [
                {
                    "title": "unknown",
                    "chart": "unknown",
                    "summary": "unknown",
                    "content": "unknown",
                    "tags": ["unknown"],
                }
            ]
    return payload


def _coerce_rule(item) -> Dict[str, str]:
    if isinstance(item, dict):
        condition = str(item.get("condition", item.get("if", item.get("when", "")))).strip()
        result = str(item.get("result", item.get("then", item.get("outcome", "")))).strip()
        if not condition and item.get("text"):
            condition = str(item["text"]).strip()
        if not result and item.get("text"):
            result = str(item["text"]).strip()
        return {
            "condition": condition,
            "result": result,
            "category": str(item.get("category", "json")),
        }

    text = str(item).strip()
    return {"condition": text, "result": text, "category": "json"}


def _coerce_term(item) -> Dict[str, str]:
    if isinstance(item, dict):
        term = str(item.get("term", item.get("name", ""))).strip()
        definition = str(item.get("definition", item.get("meaning", item.get("description", "")))).strip()
        if not term and item.get("text"):
            term = str(item["text"]).strip()
        if not definition and item.get("text"):
            definition = str(item["text"]).strip()
        return {
            "term": term,
            "definition": definition,
            "category": str(item.get("category", "json")),
        }

    text = str(item).strip()
    return {"term": text, "definition": text, "category": "json"}


def _coerce_case(item) -> Dict[str, Any]:
    if isinstance(item, dict):
        tags = item.get("tags", [])
        if isinstance(tags, str):
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        elif isinstance(tags, IterableABC):
            tags_list = [str(tag).strip() for tag in tags if str(tag).strip()]
        else:
            tags_list = []

        return {
            "title": str(item.get("title", "")).strip(),
            "chart": str(item.get("chart", "")).strip(),
            "summary": str(item.get("summary", "")).strip(),
            "content": str(item.get("content", "")).strip(),
            "tags": tags_list,
        }

    text = str(item).strip()
    return {
        "title": text,
        "chart": "",
        "summary": text[:120],
        "content": text,
        "tags": [],
    }


def extract_rules_terms_cases(path: str) -> dict:
    suffix = Path(path).suffix.lower()

    if suffix == ".json":
        structured = _load_structured_json(path)
        if set(structured.keys()) >= {"rules", "terms", "cases"}:
            raw_rules = structured.get("rules", [])
            raw_terms = structured.get("terms", [])
            raw_cases = structured.get("cases", [])
            rules = [_coerce_rule(item) for item in raw_rules] if isinstance(raw_rules, list) else []
            terms = [_coerce_term(item) for item in raw_terms] if isinstance(raw_terms, list) else []
            cases = [_coerce_case(item) for item in raw_cases] if isinstance(raw_cases, list) else []
            payload = {"rules": rules, "terms": terms, "cases": cases}
            if all(isinstance(value, list) for value in payload.values()):
                _annotate_links(payload["rules"], payload["terms"], payload["cases"])
                return _ensure_defaults(payload)
        text = structured.get("text", "")
    else:
        text = _read_text(path)

    rules = _extract_rules_from_text(text)
    terms = _extract_terms_from_text(text)
    cases = _extract_cases_from_text(text)

    payload = {"rules": rules, "terms": terms, "cases": cases}
    _annotate_links(rules, terms, cases)
    return _ensure_defaults(payload)


__all__ = ["extract_rules_terms_cases"]
