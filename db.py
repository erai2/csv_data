import sqlite3
import pandas as pd

def init_db(db_path="suri.db"):
    """
    DB 초기화: rules / concepts / cases 테이블 생성
    UNIQUE 제약 조건에서 'source'를 제외하여 내용 기반 중복을 방지합니다.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # rules 테이블 (UNIQUE 조건 변경)
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
        UNIQUE(condition_text, result_text)
    )
    """)

    # concepts 테이블 (UNIQUE 조건 변경)
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
        UNIQUE(name, definition)
    )
    """)

    # cases 테이블 (UNIQUE 조건 변경)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        saju_text TEXT,
        relations_found TEXT,
        interpretation TEXT,
        source TEXT,
        created_at TEXT,
        UNIQUE(saju_text, interpretation)
    )
    """)

    conn.commit()
    conn.close()


def insert_data(db_path, table, data: dict):
    """
    데이터 삽입 (Upsert 로직):
    - 내용이 중복될 경우(ON CONFLICT), 새로 추가하지 않고
    - 기존 항목의 'source' 필드에 새로운 출처를 추가(UPDATE)합니다.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 각 테이블의 내용 기반 UNIQUE 컬럼 정의
    unique_columns = {
        "concepts": ["name", "definition"],
        "rules": ["condition_text", "result_text"],
        "cases": ["saju_text", "interpretation"]
    }

    if table not in unique_columns:
        print(f"[WARN] '{table}'에 대한 UNIQUE 정책이 없어 기본적인 INSERT OR IGNORE를 실행합니다.")
        # (기존 로직 - 혹시 모를 다른 테이블을 위해 유지)
        cols = ",".join(data.keys())
        placeholders = ",".join(["?"]*len(data))
        sql = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
        cur.execute(sql, list(data.values()))
    else:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        conflict_target = ", ".join(unique_columns[table])
        
        # ON CONFLICT... DO UPDATE 구문
        # 1. 데이터를 INSERT 시도
        # 2. 만약 unique_columns가 중복되어 CONFLICT가 발생하면
        # 3. 기존 데이터의 source 필드를 업데이트
        #    - 단, 기존 source에 새로운 source가 포함되어 있지 않을 때만 추가 (중복 출처 방지)
        sql = f"""
            INSERT INTO {table} ({cols}) VALUES ({placeholders})
            ON CONFLICT({conflict_target}) DO UPDATE SET
                source = source || ', ' || excluded.source
            WHERE instr(source, excluded.source) = 0;
        """
        try:
            cur.execute(sql, list(data.values()))
        except Exception as e:
            print(f"[ERROR] insert_data 실패: {e}")

    conn.commit()
    conn.close()


def fetch_table(db_path="suri.db", table="rules"):
    """특정 테이블 전체 DataFrame 반환 (기존과 동일)"""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY created_at DESC", conn)
    except Exception as e:
        print(f"[ERROR] fetch_table 실패: {e}")
        df = pd.DataFrame()
    conn.close()
    return df