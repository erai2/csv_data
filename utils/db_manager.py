"""Database helpers for the explainable fortune inference system."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import sqlite3


DB_PATH = Path("data/fortune.db")


def _ensure_data_dir() -> None:
    """Make sure the SQLite directory exists before connecting."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_path() -> Path:
    """Expose the resolved database path for other modules."""
    return DB_PATH


@contextmanager
def get_connection(row_factory: Optional[type] = sqlite3.Row) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with the requested row factory."""

    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    if row_factory is not None:
        conn.row_factory = row_factory
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialise all tables required by the application."""

    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                gender TEXT,
                gan TEXT,
                zhi TEXT,
                daewoon TEXT,
                sewoon TEXT,
                structure_json TEXT,
                result_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS principles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                definition TEXT,
                category TEXT,
                UNIQUE(title, category)
            );

            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition TEXT,
                result TEXT,
                reference TEXT,
                category TEXT,
                UNIQUE(condition, result, IFNULL(reference, ""))
            );

            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relation_type TEXT,
                description TEXT,
                source TEXT,
                UNIQUE(relation_type, description)
            );

            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                source TEXT,
                UNIQUE(title, content, source)
            );

            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                chart TEXT,
                summary TEXT,
                content TEXT,
                tags TEXT,
                source TEXT,
                UNIQUE(title, summary, source)
            );
            """
        )
        conn.commit()


def record_rules(rules: Iterable[Dict[str, str]]) -> None:
    """Insert a batch of rule dictionaries into the rules table."""

    if not rules:
        return

    payload = [
        (
            rule.get("condition", "").strip(),
            rule.get("result", "").strip(),
            rule.get("reference"),
            rule.get("category"),
        )
        for rule in rules
    ]

    with get_connection(None) as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO rules (condition, result, reference, category)
            VALUES (?, ?, ?, ?)
            """,
            payload,
        )
        conn.commit()


def record_principles(principles: Iterable[Dict[str, str]]) -> None:
    """Insert principle definitions that accompany uploaded documents."""

    if not principles:
        return

    payload = [
        (
            item.get("title", "").strip(),
            item.get("definition", "").strip(),
            item.get("category", "일반"),
        )
        for item in principles
    ]

    with get_connection(None) as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO principles (title, definition, category)
            VALUES (?, ?, ?)
            """,
            payload,
        )
        conn.commit()


def record_relations(relations: Iterable[Dict[str, str]]) -> None:
    """Persist structural relations for later visualisation."""

    if not relations:
        return

    payload = [
        (
            item.get("relation_type", "").strip(),
            item.get("description", "").strip(),
            item.get("source"),
        )
        for item in relations
    ]

    with get_connection(None) as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO relations (relation_type, description, source)
            VALUES (?, ?, ?)
            """,
            payload,
        )
        conn.commit()


def record_concepts(concepts: Iterable[Dict[str, str]], source: Optional[str] = None) -> None:
    """Merge extracted concept paragraphs into the dedicated table."""

    entries = [
        (
            item.get("title", "").strip(),
            item.get("content", "").strip(),
            item.get("category", "개념"),
            (item.get("source") or source or "").strip(),
        )
        for item in concepts
        if item.get("title") or item.get("content")
    ]

    if not entries:
        return

    with get_connection(None) as conn:
        conn.executemany(
            """
            INSERT INTO concepts (title, content, category, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(title, content, source) DO UPDATE SET
                category = excluded.category
            """,
            entries,
        )
        conn.commit()


def record_cases(cases: Iterable[Dict[str, str]], source: Optional[str] = None) -> None:
    """Merge extracted case documents with preserved structure."""

    entries = [
        (
            item.get("title", "").strip(),
            item.get("chart", "").strip(),
            item.get("summary", "").strip(),
            item.get("content", "").strip(),
            ",".join(tag.strip() for tag in (item.get("tags") or []) if tag.strip()),
            (item.get("source") or source or "").strip(),
        )
        for item in cases
        if item.get("title") or item.get("content")
    ]

    if not entries:
        return

    with get_connection(None) as conn:
        conn.executemany(
            """
            INSERT INTO cases (title, chart, summary, content, tags, source)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(title, summary, source) DO UPDATE SET
                chart = excluded.chart,
                content = excluded.content,
                tags = excluded.tags
            """,
            entries,
        )
        conn.commit()


def list_rules(limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return recently stored rules."""

    query = "SELECT id, condition, result, reference, category FROM rules ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:
        cur = conn.cursor()
        if limit is None:
            rows = cur.execute(query).fetchall()
        else:
            rows = cur.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]


def list_principles(limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return principle definitions."""

    query = "SELECT id, title, definition, category FROM principles ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:
        cur = conn.cursor()
        if limit is None:
            rows = cur.execute(query).fetchall()
        else:
            rows = cur.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]


def list_relations(limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return structural relations for display or network graphs."""

    query = "SELECT id, relation_type, description, source FROM relations ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:
        cur = conn.cursor()
        if limit is None:
            rows = cur.execute(query).fetchall()
        else:
            rows = cur.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]


def list_concepts(limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return stored concept paragraphs."""

    query = "SELECT id, title, content, category, source FROM concepts ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:
        cur = conn.cursor()
        if limit is None:
            rows = cur.execute(query).fetchall()
        else:
            rows = cur.execute(query, (limit,)).fetchall()
    return [dict(row) for row in rows]


def list_cases(limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Return stored case documents."""

    query = "SELECT id, title, chart, summary, content, tags, source FROM cases ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT ?"

    with get_connection() as conn:
        cur = conn.cursor()
        if limit is None:
            rows = cur.execute(query).fetchall()
        else:
            rows = cur.execute(query, (limit,)).fetchall()

    payload: List[Dict[str, str]] = []
    for row in rows:
        record = dict(row)
        tags = record.get("tags") or ""
        record["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        payload.append(record)
    return payload


def search_concepts(keyword: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Search concept entries by keyword."""

    like = f"%{keyword}%"
    query = "SELECT id, title, content, category, source FROM concepts WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC"
    params: List[str] = [like, like]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def search_cases(keyword: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Search case entries by keyword across title, summary and content."""

    like = f"%{keyword}%"
    query = (
        "SELECT id, title, chart, summary, content, tags, source FROM cases "
        "WHERE title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ? "
        "ORDER BY id DESC"
    )
    params: List[str] = [like, like, like, like]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    payload: List[Dict[str, str]] = []
    for row in rows:
        record = dict(row)
        tags = record.get("tags") or ""
        record["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        payload.append(record)
    return payload


def search_rules(keyword: str) -> List[Dict[str, str]]:
    """Search the rules table for a keyword across the main columns."""

    like = f"%{keyword.strip()}%"
    with get_connection() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT id, condition, result, reference, category
            FROM rules
            WHERE condition LIKE ? OR result LIKE ? OR IFNULL(reference, "") LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like),
        ).fetchall()
    return [dict(row) for row in rows]


def search_relations(keyword: str) -> List[Dict[str, str]]:
    """Search stored relations by relation type or description."""

    like = f"%{keyword.strip()}%"
    with get_connection() as conn:
        cur = conn.cursor()
        rows = cur.execute(
            """
            SELECT id, relation_type, description, source
            FROM relations
            WHERE relation_type LIKE ? OR description LIKE ?
            ORDER BY id DESC
            """,
            (like, like),
        ).fetchall()
    return [dict(row) for row in rows]

