# app.py
import streamlit as st
import sqlite3
import json
from parser import parse_content
from db import init_db, insert_rule, fetch_rules
from system import Saju, Pillar, HeavenlyStem, EarthlyBranch, SajuAnalyzer

DB_PATH = "saju.db"
init_db()

st.title("📂 분석 시스템")

# --- 1. 문서 업로드 ---
uploaded_file = st.file_uploader("문서를 업로드하세요", type=["txt", "md", "csv"])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    parsed = parse_content(content)

    st.subheader("📌 파싱 결과 미리보기")
    st.json(parsed)

    # DB 저장
    for item in parsed["rules"]:
        insert_rule(
            item.get("category", "unknown"),
            item.get("title", ""),
            item.get("content", ""),
            uploaded_file.name
        )
    st.success(f"✅ {uploaded_file.name} → DB 저장 완료")

# --- 2. DB 미리보기 ---
if st.button("📑 DB 미리보기"):
    rows = fetch_rules(limit=10)
    st.write(rows)

# --- 3. Analyzer 실행 ---
st.subheader("🔮 Analyzer 실행")
if st.button("분석 실행"):
    # 예시 사주 (실제 입력 폼으로 확장 가능)
    year = Pillar(HeavenlyStem("丙"), EarthlyBranch("申"))
    month = Pillar(HeavenlyStem("丙"), EarthlyBranch("申"))
    day = Pillar(HeavenlyStem("辛"), EarthlyBranch("酉"))
    time = Pillar(HeavenlyStem("丁"), EarthlyBranch("未"))
    saju = Saju(year, month, day, time)

    analyzer = SajuAnalyzer(saju, parsed_data_path="parsed_all.json")
    report = analyzer.build_report()

    st.subheader("📋 분석 리포트")
    st.text(report)

    # JSON 저장
    with open("analysis_report.json", "w", encoding="utf-8") as f:
        json.dump({"report": report}, f, ensure_ascii=False, indent=2)
    st.download_button("⬇️ 리포트 다운로드 (JSON)", data=json.dumps({"report": report}, ensure_ascii=False, indent=2), file_name="analysis_report.json")
