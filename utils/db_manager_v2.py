import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Union


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BASE_DIR / "suri_db_system" / "schema" / "suri_db_schema.sql"
SAMPLE_DATA_DIR = BASE_DIR / "suri_db_system" / "data"


def _load_schema_sql() -> str:
    if SCHEMA_PATH.exists():
        return SCHEMA_PATH.read_text(encoding="utf-8")

    # ✅ 안전장치: 스키마 파일이 없을 때 최소 테이블 생성
    return """
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        content TEXT,
        keywords TEXT,
        example TEXT,
        source TEXT
    );
    CREATE TABLE IF NOT EXISTS terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT,
        definition TEXT,
        category TEXT,
        source TEXT
    );
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        chart TEXT,
        summary TEXT,
        content TEXT,
        tags TEXT,
        source TEXT
    );
    CREATE TABLE IF NOT EXISTS case_rule_link (
        case_id INTEGER,
        rule_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS case_term_link (
        case_id INTEGER,
        term_id INTEGER
    );
    """


def _normalize_keywords(value: Optional[Union[Sequence[str], str]]) -> str:
    if isinstance(value, (list, tuple, set)):
        return ",".join(str(item) for item in value)
    return str(value) if value else ""


def _normalize_tags(value: Optional[Union[Sequence[str], str]]) -> str:
    if isinstance(value, (list, tuple, set)):
        return ",".join(str(item) for item in value)
    return str(value) if value else ""


def _extract_link_ids(values: Optional[Iterable]) -> List[int]:
    link_ids: List[int] = []
    if not values:
        return link_ids

    for item in values:
        if isinstance(item, dict):
            candidate = item.get("id")
        else:
            candidate = item

        if candidate is None:
            continue

        try:
            link_ids.append(int(candidate))
        except (TypeError, ValueError):
            continue

    # 중복 제거(입력 순서 유지)
    return list(dict.fromkeys(link_ids))


def init_db(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    schema_sql = _load_schema_sql()

    with sqlite3.connect(path) as conn:
        conn.executescript(schema_sql)
        conn.commit()
        _bootstrap_sample_data(conn)


def insert_rule(
    conn: sqlite3.Connection,
    rule: Dict[str, object],
    *,
    auto_commit: bool = True,
) -> int:
    keywords_value = _normalize_keywords(rule.get("keywords"))
    payload = (
        rule.get("category"),
        rule.get("title")
        or rule.get("condition")
        or "",
        rule.get("content") or rule.get("result") or "",
        keywords_value,
        rule.get("example"),
        rule.get("source"),
    )

    rule_id = rule.get("id")
    if rule_id is not None:
        conn.execute(
            """
            INSERT INTO rules (id, category, title, content, keywords, example, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                category=excluded.category,
                title=excluded.title,
                content=excluded.content,
                keywords=excluded.keywords,
                example=excluded.example,
                source=excluded.source
            """,
            (rule_id,) + payload,
        )
        inserted_id = int(rule_id)
    else:
        cursor = conn.execute(
            """
            INSERT INTO rules (category, title, content, keywords, example, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        inserted_id = int(cursor.lastrowid)

    if auto_commit:
        conn.commit()
    return inserted_id


def insert_term(
    conn: sqlite3.Connection,
    term: Dict[str, object],
    *,
    auto_commit: bool = True,
) -> int:
    payload = (
        term.get("term"),
        term.get("definition"),
        term.get("category"),
        term.get("source"),
    )

    term_id = term.get("id")
    if term_id is not None:
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
            (term_id,) + payload,
        )
        inserted_id = int(term_id)
    else:
        cursor = conn.execute(
            """
            INSERT INTO terms (term, definition, category, source)
            VALUES (?, ?, ?, ?)
            """,
            payload,
        )
        inserted_id = int(cursor.lastrowid)

    if auto_commit:
        conn.commit()
    return inserted_id


def insert_case(
    conn: sqlite3.Connection,
    case: Dict[str, object],
    *,
    auto_commit: bool = True,
) -> int:
    tags_value = _normalize_tags(case.get("tags"))
    payload = (
        case.get("title"),
        case.get("chart"),
        case.get("summary"),
        case.get("content"),
        tags_value,
        case.get("source"),
    )

    case_id = case.get("id")
    if case_id is not None:
        conn.execute(
            """
            INSERT INTO cases (id, title, chart, summary, content, tags, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                chart=excluded.chart,
                summary=excluded.summary,
                content=excluded.content,
                tags=excluded.tags,
                source=excluded.source
            """,
            (case_id,) + payload,
        )
        inserted_id = int(case_id)
    else:
        cursor = conn.execute(
            """
            INSERT INTO cases (title, chart, summary, content, tags, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        inserted_id = int(cursor.lastrowid)

    # 관계 테이블 갱신
    conn.execute("DELETE FROM case_rule_link WHERE case_id = ?", (inserted_id,))
    conn.execute("DELETE FROM case_term_link WHERE case_id = ?", (inserted_id,))

    for rule_id in _extract_link_ids(case.get("linked_rules")):
        conn.execute(
            "INSERT INTO case_rule_link (case_id, rule_id) VALUES (?, ?)",
            (inserted_id, rule_id),
        )

    for term_id in _extract_link_ids(case.get("linked_terms")):
        conn.execute(
            "INSERT INTO case_term_link (case_id, term_id) VALUES (?, ?)",
            (inserted_id, term_id),
        )

    if auto_commit:
        conn.commit()
    return inserted_id


def fetch_rules(path: str) -> List[Dict[str, object]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.*, COUNT(cr.case_id) AS related_case_count
            FROM rules r
            LEFT JOIN case_rule_link cr ON r.id = cr.rule_id
            GROUP BY r.id
            ORDER BY r.id DESC
            """
        )
        rows = [dict(row) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


def fetch_terms(path: str) -> List[Dict[str, object]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT t.*, COUNT(ct.case_id) AS related_case_count
            FROM terms t
            LEFT JOIN case_term_link ct ON t.id = ct.term_id
            GROUP BY t.id
            ORDER BY t.id DESC
            """
        )
        rows = [dict(row) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


def fetch_cases(
    path: str,
    keyword: str = "",
    tag_filter: str = "전체",
) -> List[Dict[str, object]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        base_query = [
            "SELECT",
            "    c.*,",
            "    GROUP_CONCAT(r.title, '||') AS related_rule_titles,",
            "    GROUP_CONCAT(t.term, '||') AS related_terms",
            "FROM cases c",
            "LEFT JOIN case_rule_link cr ON c.id = cr.case_id",
            "LEFT JOIN rules r ON cr.rule_id = r.id",
            "LEFT JOIN case_term_link ct ON c.id = ct.case_id",
            "LEFT JOIN terms t ON ct.term_id = t.id",
            "WHERE 1=1",
        ]

        params: List[str] = []

        if keyword:
            base_query.append(
                "AND (c.title LIKE ? OR c.summary LIKE ? OR c.tags LIKE ? OR r.title LIKE ? OR t.term LIKE ?)"
            )
            keyword_like = f"%{keyword}%"
            params.extend([keyword_like, keyword_like, keyword_like, keyword_like, keyword_like])

        if tag_filter != "전체":
            base_query.append("AND c.tags LIKE ?")
            params.append(f"%{tag_filter}%")

        base_query.extend(["GROUP BY c.id", "ORDER BY c.id DESC"])

        sql = "\n".join(base_query)
        cur = conn.cursor()
        cur.execute(sql, params)

        results: List[Dict[str, object]] = []
        for row in cur.fetchall():
            record = dict(row)
            related_rules = record.pop("related_rule_titles", "") or ""
            related_terms = record.pop("related_terms", "") or ""

            record["related_rules"] = list(
                dict.fromkeys(value for value in related_rules.split("||") if value)
            )
            record["related_terms"] = list(
                dict.fromkeys(value for value in related_terms.split("||") if value)
            )
            results.append(record)

        return results
    finally:
        conn.close()


def delete_case(path: str, case_id: int) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        conn.commit()
    finally:
        conn.close()


def _bootstrap_sample_data(conn: sqlite3.Connection) -> None:
    if not SAMPLE_DATA_DIR.exists():
        return

    try:
        rule_count = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
        term_count = conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        case_count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    except sqlite3.OperationalError:
        # 스키마가 아직 생성되지 않은 경우를 방어
        return

    if rule_count or term_count or case_count:
        return

    try:
        with (SAMPLE_DATA_DIR / "rules.json").open("r", encoding="utf-8") as f:
            rules = json.load(f)
        with (SAMPLE_DATA_DIR / "terms.json").open("r", encoding="utf-8") as f:
            terms = json.load(f)
        with (SAMPLE_DATA_DIR / "cases.json").open("r", encoding="utf-8") as f:
            cases = json.load(f)
    except FileNotFoundError:
        return
    except json.JSONDecodeError:
        return

    for rule in rules:
        insert_rule(conn, rule, auto_commit=False)
    for term in terms:
        insert_term(conn, term, auto_commit=False)
    for case in cases:
        insert_case(conn, case, auto_commit=False)

    conn.commit()


__all__ = [
    "init_db",
    "insert_rule",
    "insert_term",
    "insert_case",
    "fetch_rules",
    "fetch_terms",
    "fetch_cases",
    "delete_case",
]
