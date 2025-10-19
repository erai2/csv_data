import sqlite3

conn = sqlite3.connect("data/suam_db.db")
cursor = conn.cursor()

print("📋 [테이블 목록]")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print(tables)

for table in tables:
    print(f"\n📘 {table} 구조")
    cursor.execute(f"PRAGMA table_info({table});")
    for row in cursor.fetchall():
        print(row)

    print(f"\n🔹 {table} 데이터 (최대 5개)")
    cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
    for row in cursor.fetchall():
        print(row)

conn.close()
print("\n✅ DB 상태 점검 완료")
