import pandas as pd
from db import insert_data

def save_to_csv_and_db(parsed, db_path="suri.db", out_dir="csv_refined"):
    import os
    os.makedirs(out_dir, exist_ok=True)

    for category, items in parsed.items():
        if not items:
            continue
        df = pd.DataFrame(items)
        file_path = os.path.join(out_dir, f"{category}_refined.csv")
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

        # DB 삽입
        for row in items:
            insert_data(db_path, category, row)

    return True
