# modules/db.py
# 역할: SQLite 초기화/CSV 적재/간단 검색

from __future__ import annotations
import os, sqlite3
import pandas as pd

DB_PATH = os.path.join("data","saju_data.db")

DDL = {
"rules": """
CREATE TABLE IF NOT EXISTS rules (
  rule_id TEXT PRIMARY KEY,
  keyword TEXT, description TEXT, target TEXT, category TEXT, pattern TEXT
);""",
"cases": """
CREATE TABLE IF NOT EXISTS cases (
  case_id TEXT PRIMARY KEY,
  case_name TEXT, gender TEXT, saju_structure TEXT,
  daeun_info TEXT, control_method TEXT, details TEXT
);""",
"concepts": """
CREATE TABLE IF NOT EXISTS concepts (
  concept_id TEXT PRIMARY KEY,
  description TEXT, category TEXT
);"""
}

def init_db(path: str = DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as conn:
        cur = conn.cursor()
        for sql in DDL.values(): cur.execute(sql)
        conn.commit()

def import_csv(csv_path: str, table: str, path: str = DB_PATH):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    rename = {
        "규칙ID":"rule_id","키워드":"keyword","설명":"description","적용대상":"target","카테고리":"category","패턴":"pattern",
        "사례ID":"case_id","사례명":"case_name","성별":"gender","사주구성":"saju_structure","대운정보":"daeun_info","제압방식":"control_method","상세설명":"details",
        "개념ID":"concept_id","개념명":"concept_name","카테고리":"category"
    }
    for k,v in list(rename.items()):
        if k in df.columns: df.rename(columns={k:v}, inplace=True)
    with sqlite3.connect(path) as conn:
        df.to_sql(table, conn, if_exists="append", index=False)