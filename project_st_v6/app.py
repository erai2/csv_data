import streamlit as st
from parser import parse_documents
from saju_system import SajuAnalyzer

st.title("📊 DOCU parser")

if st.button("📂 문서 파싱 실행"):
    parsed = parse_documents("docs")
    st.success("파싱 완료 → parsed/parsed_keywords.json")
    st.json(parsed)

if st.button("🔍 Analyzer 실행"):
    analyzer = SajuAnalyzer(parsed_data_path="parsed/parsed_keywords.json")
    report = analyzer.build_report()
    st.text_area("리포트", report, height=400)
