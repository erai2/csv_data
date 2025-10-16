"""SQLite 초기화 및 데이터 삽입 스크립트.

JSON 데이터(rules, terms, cases)를 읽어 수암명리 DB에 적재하고
사례-규칙, 사례-용어 연결 관계까지 생성한다.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "suri_manual.db"
SCHEMA_PATH = BASE_DIR / "schema" / "suri_db_schema.sql"
DATA_DIR = BASE_DIR / "data"


def init_db() -> None:
    """스키마 파일을 실행하여 DB를 초기화한다."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)
        conn.commit()
    print("✅ DB 초기화 완료")


def load_json_data(filename: str) -> List[dict]:
    """data 디렉터리에서 JSON 데이터를 로드한다."""
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    if not isinstance(data, list):
        raise ValueError(f"{filename} 파일은 리스트 형태의 JSON이어야 합니다.")
    return data


def normalize_keywords(value) -> str:
    if isinstance(value, list):
        return ",".join(value)
    return value or ""


def insert_rules(conn: sqlite3.Connection, rules: Iterable[dict]) -> Dict[int, int]:
    """규칙 데이터를 삽입하고 JSON id → DB id 매핑을 반환한다."""
    id_map: Dict[int, int] = {}
    for record in rules:
        payload = (
            normalize_keywords(record.get("keywords")),
            record.get("category"),
            record.get("title"),
            record.get("content"),
            record.get("example"),
            record.get("source"),
        )

        if record.get("id") is not None:
            conn.execute(
                """
                INSERT INTO rules (id, keywords, category, title, content, example, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    keywords=excluded.keywords,
                    category=excluded.category,
                    title=excluded.title,
                    content=excluded.content,
                    example=excluded.example,
                    source=excluded.source
                """,
                (record["id"],) + payload,
            )
            db_id = int(record["id"])
        else:
            cursor = conn.execute(
                """
                INSERT INTO rules (keywords, category, title, content, example, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
            db_id = cursor.lastrowid

        if record.get("id") is not None:
            id_map[int(record["id"])] = db_id
    return id_map


def insert_terms(conn: sqlite3.Connection, terms: Iterable[dict]) -> Dict[int, int]:
    """용어 데이터를 삽입하고 JSON id → DB id 매핑을 반환한다."""
    id_map: Dict[int, int] = {}
    for record in terms:
        payload = (
            record.get("term"),
            record.get("definition"),
            record.get("category"),
            record.get("source"),
        )

        if record.get("id") is not None:
            conn.execute(
                """
                INSERT INTO terms (id, term, definition, category, source)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    term=excluded.term,
                    definition=excluded.definition,
                    category=excluded.category,
                    source=excluded.source
                """,
                (record["id"],) + payload,
            )
            db_id = int(record["id"])
        else:
            cursor = conn.execute(
                """
                INSERT INTO terms (term, definition, category, source)
                VALUES (?, ?, ?, ?)
                """,
                payload,
            )
            db_id = cursor.lastrowid

        if record.get("id") is not None:
            id_map[int(record["id"])] = db_id
    return id_map


def insert_cases(
    conn: sqlite3.Connection,
    cases: Iterable[dict],
    rule_id_map: Dict[int, int],
    term_id_map: Dict[int, int],
) -> None:
    """사례 데이터를 삽입하고 관계 테이블을 채운다."""
    for record in cases:
        tags = record.get("tags")
        tags_value = ",".join(tags) if isinstance(tags, list) else (tags or "")

        cursor = conn.execute(
            """
            INSERT INTO cases (title, chart, summary, content, tags, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.get("title"),
                record.get("chart"),
                record.get("summary"),
                record.get("content"),
                tags_value,
                record.get("source"),
            ),
        )
        case_id = cursor.lastrowid

        for json_rule_id in record.get("linked_rules", []):
            rule_id = rule_id_map.get(json_rule_id, json_rule_id)
            conn.execute(
                "INSERT INTO case_rule_link (case_id, rule_id) VALUES (?, ?)",
                (case_id, rule_id),
            )

        for json_term_id in record.get("linked_terms", []):
            term_id = term_id_map.get(json_term_id, json_term_id)
            conn.execute(
                "INSERT INTO case_term_link (case_id, term_id) VALUES (?, ?)",
                (case_id, term_id),
            )


def main() -> None:
    init_db()

    rules = load_json_data("rules.json")
    terms = load_json_data("terms.json")
    cases = load_json_data("cases.json")

    with sqlite3.connect(DB_PATH) as conn:
        rule_map = insert_rules(conn, rules)
        term_map = insert_terms(conn, terms)
        insert_cases(conn, cases, rule_map, term_map)
        conn.commit()

    print("✅ 데이터 삽입 완료")


if __name__ == "__main__":
    main()
