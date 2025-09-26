# app.py
import streamlit as st
from parser import parse_content
from db import init_db, insert_rule, fetch_rules

# DB 초기화
init_db()

st.title("📂 업로드 & DB 저장")

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

if st.button("📑 DB 미리보기"):
    rows = fetch_rules(limit=10)
    st.write(rows)
