import streamlit as st
import pandas as pd
from parser import parse_content
from converter import save_to_csv_and_db
from db import init_db, fetch_table

DB_PATH = "suri.db"
init_db(DB_PATH)

st.title("📂 분석 & DB 저장")

tab1, tab2 = st.tabs(["문서 업로드", "DB 조회"])

with tab1:
    uploaded_file = st.file_uploader("문서를 업로드하세요", type=["txt", "md"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        parsed = parse_content(text, source=uploaded_file.name)

        st.subheader("📌 파싱 결과 미리보기")
        st.json(parsed)

        if st.button("DB 저장"):
            save_to_csv_and_db(parsed, DB_PATH)
            st.success("✅ DB 및 CSV 저장 완료!")

with tab2:
    st.subheader("📊 저장된 데이터 조회")
    table = st.selectbox("조회할 테이블", ["rules", "concepts", "cases"])
    df = fetch_table(DB_PATH, table)
    if not df.empty:
        st.dataframe(df, width="stretch")
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 CSV 다운로드", csv, f"{table}_backup.csv", "text/csv")
    else:
        st.info("아직 데이터가 없습니다.")
