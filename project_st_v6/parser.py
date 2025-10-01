"""Utilities for parsing domain documents into structured data."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Union


TEXT_EXTENSIONS = {".txt", ".md", ".csv"}


def parse_content(content: str) -> Dict[str, List[Dict[str, str]]]:
    """간단한 패턴 매칭을 사용해 문서 내용에서 규칙 후보를 추출합니다."""

    rules: List[Dict[str, str]] = []

    pattern = re.compile(r"([^\s]+의\s?(상|법|원리|의미))")
    for match in pattern.finditer(content):
        title = match.group(1)
        snippet = content[max(0, match.start() - 50): match.end() + 100]
        rules.append(
            {
                "category": "rule",
                "title": title,
                "content": snippet.strip(),
            }
        )

    return {"rules": rules}


def _normalize_json_rules(data: Union[Dict, List], source: str) -> Dict[str, List[Dict[str, str]]]:
    """사전에 작성된 JSON 문서를 규칙 리스트로 맞춰줍니다."""

    rules: List[Dict[str, str]] = []

    if isinstance(data, dict):
        candidates: Iterable = ()
        if isinstance(data.get("rules"), dict):
            candidates = data["rules"].items()
        elif isinstance(data.get("rules"), list):
            # 이미 표준 구조
            for entry in data["rules"]:
                if isinstance(entry, dict):
                    rules.append(
                        {
                            "category": entry.get("category", "unknown"),
                            "title": entry.get("title", entry.get("category", "")),
                            "content": entry.get("content", ""),
                            "source": source,
                        }
                    )
            candidates = ()
        else:
            candidates = data.items()

        for key, value in candidates:
            if key == "rules":
                continue

            description_parts: List[str] = []
            if isinstance(value, dict):
                if "description" in value:
                    description_parts.append(str(value["description"]))

                extra = {k: v for k, v in value.items() if k not in {"description", "title"}}
                if extra:
                    description_parts.append(json.dumps(extra, ensure_ascii=False, indent=2))

                title = value.get("title", key)
            else:
                title = key
                description_parts.append(str(value))

            rules.append(
                {
                    "category": str(key),
                    "title": str(title),
                    "content": "\n".join(part for part in description_parts if part).strip(),
                    "source": source,
                }
            )

    elif isinstance(data, list):
        for entry in data:
            rules.append(
                {
                    "category": "list_item",
                    "title": str(entry),
                    "content": str(entry),
                    "source": source,
                }
            )

    return {"rules": rules}


def parse_documents(directory: Union[str, Path], save_path: Union[str, Path] = "parsed_all.json") -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """`directory` 아래의 문서를 순회하면서 규칙 데이터를 생성합니다."""

    docs_dir = Path(directory)
    parsed_output: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

    if not docs_dir.exists():
        return parsed_output

    for file_path in sorted(docs_dir.iterdir()):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        if suffix in TEXT_EXTENSIONS:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            parsed = parse_content(content)
            for rule in parsed.get("rules", []):
                rule.setdefault("source", file_path.name)
            parsed_output[file_path.name] = parsed
        elif suffix == ".json":
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {"rules": []}
            parsed_output[file_path.name] = _normalize_json_rules(data, file_path.name)

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    to_dump = parsed_output if parsed_output else {}
    save_path.write_text(
        json.dumps(to_dump, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return parsed_output


def save_parsed(data, filename: Union[str, Path] = "parsed_all.json") -> None:
    """Streamlit UI에서 직접 저장할 때 사용."""

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
