import os, json

def merge_rules_to_master():
    rules_dir = "rules"
    merged = {}
    os.makedirs(rules_dir, exist_ok=True)

    for file in os.listdir(rules_dir):
        if file.endswith(".json") and "master" not in file:
            path = os.path.join(rules_dir, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
            except Exception as e:
                print(f"⚠️ {file} 불러오기 실패: {e}")

    master_path = os.path.join(rules_dir, "rules_master.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # 백업 저장
    backup_path = os.path.join(rules_dir, "rules_master_backup.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    return merged
