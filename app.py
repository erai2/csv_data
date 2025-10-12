import os
import sqlite3

import streamlit as st

from utils.db_manager import (
    fetch_inferences,
    fetch_rules,
    fetch_terms,
    init_db,
    insert_chart,
    insert_inference,
    insert_rule,
    insert_term,
)
from utils.extractor_v2 import extract_rules_and_terms
from utils.interpreter_v2 import analyze_chart
from utils.logic_engine import infer_logic
from utils.visualize import draw_chart_relations

st.set_page_config(page_title="명리 자동 해석 시스템", layout="wide")

DB_PATH = os.path.join("data", "suri_analysis.db")
init_db(DB_PATH)

st.title("📘 명리 자동 해석 시스템 v10.5")

# Tab order: 3-4-2-1-5 (document upload, rule search, glossary, interpretation, visualization)
tabs = st.tabs(
    [
        "📄 문서 업로드",
        "🔍 조건·규칙 검색",
        "📘 용어 사전",
        "🪶 명조 해석",
        "🌐 명조 구조 시각화",
    ]
)


# ------------------------------------------------------------
# 3️⃣ 문서 업로드
# ------------------------------------------------------------
with tabs[0]:
    st.header("📄 문서 업로드 및 자동 추출")
    uploaded_file = st.file_uploader(
        "문서를 업로드하세요", type=["txt", "docx", "pdf", "zip"]
    )
    if uploaded_file:
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        extracted = extract_rules_and_terms(save_path)
        st.success(
            f"{len(extracted['rules'])}개 규칙, {len(extracted['terms'])}개 용어 추출 완료!"
        )

        conn = sqlite3.connect(DB_PATH)
        for rule in extracted["rules"]:
            insert_rule(conn, rule)
        for term in extracted["terms"]:
            insert_term(conn, term)
        conn.close()

        st.json(extracted)


# ------------------------------------------------------------
# 4️⃣ 조건·규칙 검색
# ------------------------------------------------------------
with tabs[1]:
    st.header("🔍 조건·규칙 검색")
    keyword = st.text_input("검색어 입력 (예: 午卯破, 合留, 官印相生格)")
    if st.button("검색"):
        results = fetch_rules(DB_PATH, keyword)
        st.write(f"검색 결과 {len(results)}건")
        for rule in results:
            st.markdown(f"**[{rule['category']}]** {rule['condition']} → {rule['result']}")
            if rule.get("description"):
                st.caption(rule["description"])
            if rule.get("source"):
                st.caption(f"출처: {rule['source']}")


# ------------------------------------------------------------
# 2️⃣ 용어 사전
# ------------------------------------------------------------
with tabs[2]:
    st.header("📘 용어 사전")
    term_keyword = st.text_input("용어 검색 (예: 比劫, 財破, 庫開)")
    if st.button("용어 검색"):
        terms = fetch_terms(DB_PATH, term_keyword)
        if not terms:
            st.warning("결과 없음")
        for term in terms:
            st.markdown(f"### {term['term']}")
            st.write(term["definition"])
            st.caption(f"분류: {term['category']}")


# ------------------------------------------------------------
# 1️⃣ 명조 해석
# ------------------------------------------------------------
with tabs[3]:
    st.header("🪶 명조 해석")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("이름", "")
        gender = st.selectbox("성별", ["坤(여)", "乾(남)"])
    with col2:
        gan = st.text_input("천간 (시 일 월 년)", "丁 戊 辛 辛")
    with col3:
        zhi = st.text_input("지지 (시 일 월 년)", "午 卯 亥 ⺒")

    if st.button("해석 실행"):
        chart = analyze_chart(gan, zhi)
        st.subheader("🌿 구조 분석 결과")
        st.json(chart)

        st.subheader("🧠 자동 해석 결과")
        inferred = infer_logic(chart)
        st.table(inferred)

        insert_chart(DB_PATH, name, gender, gan, zhi, chart)
        insert_inference(DB_PATH, name, inferred)
        st.success("DB 저장 완료!")

        if name:
            history = fetch_inferences(DB_PATH, name)
            if history:
                st.subheader("🗂️ 과거 해석 기록")
                for record in history:
                    st.markdown(
                        f"- {record['chart_name']} (ID: {record['id']})"
                    )


# ------------------------------------------------------------
# 5️⃣ 명조 구조 시각화
# ------------------------------------------------------------
with tabs[4]:
    st.header("🌐 명조 구조 시각화 (합·충·형·파·묘)")
    chart_name = st.text_input("시각화할 명조 이름 입력")
    if st.button("시각화 실행"):
        relations = [
            ("午", "卯", "破"),
            ("卯", "亥", "合"),
            ("戌", "辰", "沖"),
        ]
        html_path = draw_chart_relations(chart_name or "chart", relations)
        with open(html_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600, scrolling=True)

        st.success("시각화 완료!")
