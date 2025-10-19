import sqlite3
from pathlib import Path

DB_PATH = Path("data/suam_db.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db(schema_file="data/suam_db_schema.sql"):
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Suri 명리 DB initialized successfully.")

def insert_data(table, data: dict):
    conn = get_connection()
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def query_data(table, where=None):
    conn = get_connection()
    sql = f"SELECT * FROM {table}"
    if where:
        sql += f" WHERE {where}"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(row) for row in rows]
