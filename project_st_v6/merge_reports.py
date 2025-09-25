# merge_reports.py
import os
def merge_reports(folder="reports",out="reports/merged_report.md"):
    if not os.path.exists(folder): return None
    texts=[]
    for fn in os.listdir(folder):
        if fn.endswith(".md"):
            with open(os.path.join(folder,fn),encoding="utf-8") as f: texts.append(f.read())
    merged="\n\n---\n\n".join(texts)
    with open(out,"w",encoding="utf-8") as f:f.write(merged)
    return out
