# modules/utils.py
# 역할: 경로/저장/병기/YAML 로더/품질 리포트 생성

from __future__ import annotations
import os, json
from datetime import datetime
from typing import Dict, Any, Tuple
import pandas as pd
import yaml

RULE_COLS   = ['규칙ID','키워드','설명','적용대상','카테고리','패턴']
CASE_COLS   = ['사례ID','사례명','성별','사주구성','대운정보','제압방식','상세설명']
CONCEPT_COLS= ['개념ID','개념명','설명','카테고리']

DATA_DIR = "data"
IN_DIR   = os.path.join(DATA_DIR,"input")
OUT_DIR  = os.path.join(DATA_DIR,"output")
MAP_DIR  = os.path.join(DATA_DIR,"mappings")
PATTERN_PATH = os.path.join(MAP_DIR,"patterns.yaml")
HANJA_PATH   = os.path.join(MAP_DIR,"hanja_map.json")

def ensure_dirs():
    os.makedirs(IN_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MAP_DIR, exist_ok=True)

def now_tag()->str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def load_patterns(path: str = PATTERN_PATH)->Dict[str,Any]:
    if not os.path.exists(path): return {"cases": [], "rules": [], "concepts": []}
    with open(path,"r",encoding="utf-8") as f: data = yaml.safe_load(f) or {}
    data.setdefault("cases",[]); data.setdefault("rules",[]); data.setdefault("concepts",[])
    return data

def load_hanja_map(path: str = HANJA_PATH)->Dict[str,str]:
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    return {
        "대운":"大運","세운":"歲運","응기":"應期","록":"祿","원신":"原神","원국":"原局",
        "합":"合","충":"沖","형":"刑","파":"破","천":"穿","입묘":"入墓",
        "갑":"甲","을":"乙","병":"丙","정":"丁","무":"戊","기":"己","경":"庚","신":"辛","임":"壬","계":"癸",
        "자":"子","축":"丑","인":"寅","묘":"卯","진":"辰","사":"巳","오":"午","미":"未","신(申)":"申","유":"酉","술":"戌","해":"亥"
    }

def format_korean_chinese(text: str, hanja_map: Dict[str,str])->str:
    if not text: return text
    out = text
    for ko, han in hanja_map.items():
        if f"{ko}(" in out: continue
        out = out.replace(ko, f"{ko}({han})")
    return out

def apply_bilingual(df: pd.DataFrame, hanja_map: Dict[str,str])->pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: format_korean_chinese(x, hanja_map) if pd.notna(x) else x)
    return df

def save_csvs(rules: pd.DataFrame, cases: pd.DataFrame, concepts: pd.DataFrame, out_dir: str = OUT_DIR)->Dict[str,str]:
    os.makedirs(out_dir, exist_ok=True)
    tag = now_tag()
    paths = {
        "rules":    os.path.join(out_dir, f"rules_{tag}.csv"),
        "cases":    os.path.join(out_dir, f"cases_{tag}.csv"),
        "concepts": os.path.join(out_dir, f"concepts_{tag}.csv"),
    }
    rules.to_csv(paths["rules"], index=False, encoding="utf-8-sig")
    cases.to_csv(paths["cases"], index=False, encoding="utf-8-sig")
    concepts.to_csv(paths["concepts"], index=False, encoding="utf-8-sig")
    return paths

# ── v2: 품질 리포트 ─────────────────────────────────────────────────────
def quality_report(rules: pd.DataFrame, cases: pd.DataFrame, concepts: pd.DataFrame)->Tuple[str, str]:
    """리포트 문자열과 저장 경로 반환"""
    def miss_rate(df: pd.DataFrame):
        return {c: int(df[c].isna().sum() + (df[c]=="" ).sum()) for c in df.columns}

    from collections import Counter
    r_dup = [k for k, v in Counter(rules.get("규칙ID", pd.Series())).items() if v>1]
    c_dup = [k for k, v in Counter(cases.get("사례ID", pd.Series())).items() if v>1]
    k_dup = [k for k, v in Counter(concepts.get("개념ID", pd.Series())).items() if v>1]

    # 사례 필수 점검(간/지 라인 유무)
    case_missing_saju = cases[(~cases["사주구성"].astype(str).str.contains(r"[甲乙丙丁戊己庚辛壬癸]")) |
                              (~cases["사주구성"].astype(str).str.contains(r"[子丑寅卯辰巳午未申酉戌亥]"))]

    md = []
    md.append("# 품질 리포트")
    md.append(f"- 규칙: {len(rules)}행, 사례: {len(cases)}행, 개념: {len(concepts)}행")
    md.append("\n## 누락 필드 개수")
    md.append(f"- 규칙: {miss_rate(rules)}")
    md.append(f"- 사례: {miss_rate(cases)}")
    md.append(f"- 개념: {miss_rate(concepts)}")
    md.append("\n## 중복 ID")
    md.append(f"- 규칙ID 중복: {r_dup or '없음'}")
    md.append(f"- 사례ID 중복: {c_dup or '없음'}")
    md.append(f"- 개념ID 중복: {k_dup or '없음'}")
    md.append("\n## 사례 사주구성 점검(간/지 미검출)")
    md.append(f"- 건수: {len(case_missing_saju)}")
    if not case_missing_saju.empty:
        md.append(case_missing_saju[["사례ID","사례명","사주구성"]].to_csv(index=False))
    report_text = "\n".join(md)

    out_path = os.path.join(OUT_DIR, f"report_{now_tag()}.md")
    with open(out_path,"w",encoding="utf-8") as f: f.write(report_text)
    return report_text, out_path