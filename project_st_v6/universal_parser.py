# universal_parser.py
import os,re,json
from collections import defaultdict

def parse_documents(folder="docs"):
    parsed=defaultdict(list)
    if not os.path.exists(folder): return parsed
    for fn in os.listdir(folder):
        if not fn.endswith((".txt",".md")): continue
        txt=open(os.path.join(folder,fn),encoding="utf-8").read()
        if "묘고" in txt: parsed["묘고"].append({"file":fn,"rule":"묘고 규칙"})
        if "허실" in txt: parsed["허실"].append({"file":fn,"rule":"허실 규칙"})
        if "충" in txt: parsed["충"].append({"file":fn,"rule":"충 규칙"})
        if "합" in txt: parsed["합"].append({"file":fn,"rule":"합 규칙"})
    with open("parsed_all.json","w",encoding="utf-8") as f: json.dump(parsed,f,ensure_ascii=False,indent=2)
    return parsed
