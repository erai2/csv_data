import sqlite3
import pandas as pd

def init_db(db_path="suri.db"):
    """DB 초기화: rules / concepts / cases 테이블 생성"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # rules 테이블
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

    # concepts 테이블
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

    # cases 테이블
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
    """중복 방지 insert (UNIQUE + INSERT OR IGNORE)"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = ",".join(data.keys())
    placeholders = ",".join(["?"]*len(data))
    sql = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
    try:
        cur.execute(sql, list(data.values()))
    except Exception as e:
        print(f"[ERROR] insert_data 실패: {e}")
    conn.commit()
    conn.close()


def fetch_table(db_path="saju.db", table="rules"):
    """특정 테이블 전체 DataFrame 반환"""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY created_at DESC", conn)
    except Exception as e:
        print(f"[ERROR] fetch_table 실패: {e}")
        df = pd.DataFrame()
    conn.close()
    return df
