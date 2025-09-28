import streamlit as st
import pandas as pd
from parser import parse_content
from converter import save_to_csv_and_db
from db import init_db, fetch_table

DB_PATH = "suri.db"
init_db(DB_PATH)

st.set_page_config(page_title="분석 시스템", layout="wide")
st.title("📂 문서 → DB/CSV 저장 & 분석")

# --- 탭 구성 ---
tab1, tab2 = st.tabs(["📑 문서 업로드", "📊 DB 조회"])

# --- 1️⃣ 문서 업로드 ---
with tab1:
    uploaded_file = st.file_uploader("문서를 업로드하세요", type=["txt", "md", "docx"])
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        parsed = parse_content(text, source=uploaded_file.name)

        st.subheader("📌 파싱 결과 미리보기")
        st.json(parsed)

        if st.button("DB 저장"):
            save_to_csv_and_db(parsed, DB_PATH)
            st.success("✅ DB 및 CSV 저장 완료!")

# --- 2️⃣ DB 조회 ---
with tab2:
    st.subheader("📊 저장된 데이터 조회")

    table = st.selectbox("조회할 테이블", ["rules", "concepts", "cases"])
    df = fetch_table(DB_PATH, table)

    if not df.empty:
        # 검색어 필터
        keyword = st.text_input("🔍 키워드 검색")
        if keyword:
            df = df[df.apply(lambda row: keyword in row.to_string(), axis=1)]

        # 결과 출력
        st.dataframe(df, width="stretch")

        # CSV 다운로드
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"{table}_backup.csv",
            mime="text/csv"
        )

        # Excel 다운로드
        excel_path = f"{table}_backup.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        with open(excel_path, "rb") as f:
            st.download_button(
                label="📥 Excel 다운로드",
                data=f,
                file_name=excel_path,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("아직 DB에 저장된 데이터가 없습니다.")

