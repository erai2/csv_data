import json
import os
import sqlite3
from typing import Any, Dict, List


def init_db(path: str) -> None:
    """Initialize database schema if it does not exist."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition TEXT,
            result TEXT,
            category TEXT,
            description TEXT,
            source TEXT
        );
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            definition TEXT,
            category TEXT
        );
        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            gan TEXT,
            zhi TEXT,
            structure TEXT
        );
        CREATE TABLE IF NOT EXISTS inferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_name TEXT,
            result_json TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def insert_rule(conn: sqlite3.Connection, rule: Dict[str, Any]) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO rules (condition, result, category, description, source)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            rule.get("condition"),
            rule.get("result"),
            rule.get("category"),
            rule.get("description"),
            rule.get("source"),
        ),
    )
    conn.commit()


def insert_term(conn: sqlite3.Connection, term: Dict[str, Any]) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO terms (term, definition, category)
        VALUES (?, ?, ?)
        """,
        (
            term.get("term"),
            term.get("definition"),
            term.get("category"),
        ),
    )
    conn.commit()


def fetch_rules(path: str, keyword: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM rules
        WHERE condition LIKE ? OR result LIKE ? OR description LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def fetch_terms(path: str, keyword: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM terms
        WHERE term LIKE ? OR definition LIKE ? OR category LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def insert_chart(
    path: str,
    name: str,
    gender: str,
    gan: str,
    zhi: str,
    structure: Dict[str, Any],
) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        INSERT INTO charts (name, gender, gan, zhi, structure)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, gender, gan, zhi, json.dumps(structure, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def insert_inference(path: str, name: str, result: List[Dict[str, Any]]) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        INSERT INTO inferences (chart_name, result_json)
        VALUES (?, ?)
        """,
        (name, json.dumps(result, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def fetch_inferences(path: str, name: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM inferences WHERE chart_name = ? ORDER BY id DESC
        """,
        (name,),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
