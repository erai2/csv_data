import os
import sqlite3
from typing import Dict, Iterable, List


def init_db(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition TEXT,
                result TEXT,
                category TEXT
            );
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT,
                definition TEXT,
                category TEXT
            );
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                chart TEXT,
                summary TEXT,
                content TEXT,
                tags TEXT
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_rule(conn: sqlite3.Connection, rule: Dict[str, str]) -> None:
    conn.execute(
        "INSERT INTO rules (condition, result, category) VALUES (?, ?, ?)",
        (rule.get("condition"), rule.get("result"), rule.get("category")),
    )
    conn.commit()


def insert_term(conn: sqlite3.Connection, term: Dict[str, str]) -> None:
    conn.execute(
        "INSERT INTO terms (term, definition, category) VALUES (?, ?, ?)",
        (term.get("term"), term.get("definition"), term.get("category")),
    )
    conn.commit()


def insert_case(conn: sqlite3.Connection, case: Dict[str, Iterable[str]]) -> None:
    tags = case.get("tags", [])
    if isinstance(tags, str):
        tags_value = tags
    else:
        tags_value = ",".join(tags)

    conn.execute(
        "INSERT INTO cases (title, chart, summary, content, tags) VALUES (?, ?, ?, ?, ?)",
        (
            case.get("title"),
            case.get("chart"),
            case.get("summary"),
            case.get("content"),
            tags_value,
        ),
    )
    conn.commit()


def fetch_rules(path: str) -> List[Dict[str, str]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM rules ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def fetch_terms(path: str) -> List[Dict[str, str]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM terms ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def fetch_cases(path: str, keyword: str = "", tag_filter: str = "전체") -> List[Dict[str, str]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        base_query = "SELECT * FROM cases WHERE 1=1"
        params: List[str] = []

        if keyword:
            base_query += " AND (title LIKE ? OR summary LIKE ? OR tags LIKE ?)"
            keyword_like = f"%{keyword}%"
            params.extend([keyword_like, keyword_like, keyword_like])

        if tag_filter != "전체":
            base_query += " AND tags LIKE ?"
            params.append(f"%{tag_filter}%")

        base_query += " ORDER BY id DESC"

        cur = conn.cursor()
        cur.execute(base_query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def delete_case(path: str, case_id: int) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        conn.commit()
    finally:
        conn.close()


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
