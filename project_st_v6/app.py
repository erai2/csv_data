# app.py
import streamlit as st
import os
import json
from parser import parse_documents
from analyzer import SajuAnalyzer

st.set_page_config(page_title="Saju Analyzer", layout="wide")

st.title("📚 수암명리 문헌 분석 시스템")

# --- Step 1: 파일 업로드 ---
st.header("1️⃣ 문서 업로드 & 파싱")

uploaded_files = st.file_uploader("문서 파일 업로드 (.txt, .md)", type=["txt", "md"], accept_multiple_files=True)

if uploaded_files:
    os.makedirs("docs", exist_ok=True)
    for file in uploaded_files:
        filepath = os.path.join("docs", file.name)
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
    st.success(f"{len(uploaded_files)}개 파일 저장 완료 → docs/ 폴더")

    if st.button("📂 Parse Documents"):
        parsed = parse_documents("docs")
        st.success("✅ parsed_all.json 저장 완료")
        st.json(parsed)

# --- Step 2: Analyzer 실행 ---
st.header("2️⃣ Analyzer 실행")

if st.button("🔍 Run Analyzer"):
    analyzer = SajuAnalyzer(parsed_data_path="parsed_all.json")
    report = analyzer.build_report()

    # 화면에 출력
    st.subheader("📑 분석 결과 (미리보기)")
    st.text_area("Report", report[:2000], height=400)

    # 카테고리별 요약
    st.subheader("📊 카테고리별 요약")
    st.text(analyzer.summarize_by_category())

    # 저장
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    st.success("✅ analysis_report.md 저장 완료")
