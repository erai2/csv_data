import sqlite3
import pandas as pd

def init_db(db_path="suri.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id TEXT,
        condition_text TEXT,
        result_text TEXT,
        relation_type TEXT,
        ohaeng TEXT,
        source TEXT,
        created_at TEXT,
        UNIQUE(condition_text, result_text, source)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS concepts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id TEXT,
        name TEXT,
        definition TEXT,
        example TEXT,
        related_rules TEXT,
        source TEXT,
        created_at TEXT,
        UNIQUE(name, definition, source)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        saju_text TEXT,
        relations_found TEXT,
        interpretation TEXT,
        source TEXT,
        created_at TEXT,
        UNIQUE(saju_text, interpretation, source)
    )
    """)

    conn.commit()
    conn.close()

def insert_data(db_path, table, data: dict):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = ",".join(data.keys())
    placeholders = ",".join(["?"]*len(data))
    sql = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
    cur.execute(sql, list(data.values()))
    conn.commit()
    conn.close()

def fetch_table(db_path="saju.db", table="rules"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY created_at DESC", conn)
    conn.close()
    return df
