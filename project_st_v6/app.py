import streamlit as st
import sqlite3
import json
from parser import parse_content, save_parsed
from db import init_db, insert_rule, fetch_rules
from system import Saju, Pillar, HeavenlyStem, EarthlyBranch, SajuAnalyzer

DB_PATH = "saju.db"
init_db()

st.title("📂 분석 시스템")

# --- 1. 문서 업로드 ---
uploaded_file = st.file_uploader("문서를 업로드하세요", type=["txt", "md", "csv"])
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    parsed = parse_content(content)

    st.subheader("📌 파싱 결과 미리보기")
    st.json(parsed)

    if st.button("💾 parsed_all.json 저장"):
        save_parsed(parsed, "parsed_all.json")
        st.success("✅ parsed_all.json 저장 완료")

    if st.button("📥 DB 저장"):
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

HEAVENLY_STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
EARTHLY_BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

with st.form("saju_input_form"):
    col1, col2 = st.columns(2)

    with col1:
        year_stem = st.selectbox("년간", HEAVENLY_STEMS, index=2)   # 기본: 丙
        month_stem = st.selectbox("월간", HEAVENLY_STEMS, index=2)  # 기본: 丙
        day_stem = st.selectbox("일간", HEAVENLY_STEMS, index=7)    # 기본: 辛
        time_stem = st.selectbox("시간", HEAVENLY_STEMS, index=3)   # 기본: 丁

    with col2:
        year_branch = st.selectbox("년지", EARTHLY_BRANCHES, index=8)   # 기본: 申
        month_branch = st.selectbox("월지", EARTHLY_BRANCHES, index=8)  # 기본: 申
        day_branch = st.selectbox("일지", EARTHLY_BRANCHES, index=9)    # 기본: 酉
        time_branch = st.selectbox("시지", EARTHLY_BRANCHES, index=7)   # 기본: 未

    run_btn = st.form_submit_button("분석 실행")

if run_btn:
    try:
        year = Pillar(year_stem, year_branch)
        month = Pillar(month_stem, month_branch)
        day = Pillar(day_stem, day_branch)
        time = Pillar(time_stem, time_branch)
        saju = Saju(year, month, day, time)

        analyzer = SajuAnalyzer(saju, parsed_data_path="parsed_all.json")
        report = analyzer.build_report()

        st.subheader("📋 분석 리포트")
        st.text(report)

        st.download_button(
            "⬇️ 리포트 다운로드 (JSON)",
            data=json.dumps({"report": report}, ensure_ascii=False, indent=2),
            file_name="analysis_report.json"
        )
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
