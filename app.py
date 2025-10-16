import os
import sqlite3
from pathlib import Path

import streamlit as st

from utils.db_manager_v2 import (
    delete_case,
    fetch_cases,
    fetch_rules,
    fetch_terms,
    init_db,
    insert_case,
    insert_rule,
    insert_term,
)
from utils.extractor_v4 import extract_rules_terms_cases
from utils.visualize import draw_chart_relations

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "suri_db_system" / "db" / "suri_manual.db")
init_db(DB_PATH)

st.set_page_config(page_title="명리 자동 해석 시스템 v10.8", layout="wide")
st.title("📘 명리 자동 해석 시스템 v10.8")

TABS = st.tabs(
    [
        "📄 문서 업로드 (자동 정리)",
        "📂 사례 보기/삭제",
        "📘 용어 정리",
        "🔍 규칙 보기",
        "🌐 시각화",
    ]
)


# ------------------------------------------------------------
# 📄 1. 문서 업로드
# ------------------------------------------------------------
with TABS[0]:
    st.header("📄 문서 업로드 및 자동 구조화")
    uploaded = st.file_uploader(
        "문서를 업로드하세요", type=["txt", "docx", "pdf", "zip"]
    )
    if uploaded is not None:
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, uploaded.name)
        with open(save_path, "wb") as f:
            f.write(uploaded.read())

        extracted = extract_rules_terms_cases(save_path)

        st.success(
            "✅ {case_count}개 사례 / {rule_count}개 규칙 / {term_count}개 용어 자동 추출".format(
                case_count=len(extracted.get("cases", [])),
                rule_count=len(extracted.get("rules", [])),
                term_count=len(extracted.get("terms", [])),
            )
        )

        with st.expander("🧩 규칙 요약", expanded=True):
            rules_data = extracted.get("rules", [])
            if rules_data:
                st.dataframe(rules_data)
            else:
                st.info("추출된 규칙이 없습니다.")

        with st.expander("📘 용어 정리", expanded=False):
            terms_data = extracted.get("terms", [])
            if terms_data:
                st.dataframe(terms_data)
            else:
                st.info("추출된 용어가 없습니다.")

        with st.expander("📂 사례 목록", expanded=True):
            cases_data = extracted.get("cases", [])
            if not cases_data:
                st.info("추출된 사례가 없습니다.")
            for case_index, case in enumerate(cases_data):
                with st.expander(f"📁 {case.get('title', '사례')}", expanded=False):
                    st.markdown(f"**명조:** {case.get('chart', '-')}")
                    st.markdown(f"**요약:** {case.get('summary', '요약 없음')}")
                    st.text_area(
                        "본문",
                        case.get("content", ""),
                        height=250,
                        key=f"case_content_{case_index}",
                    )
                    tags = case.get("tags", [])
                    if isinstance(tags, (list, tuple)):
                        tag_label = ", ".join(tags)
                    else:
                        tag_label = str(tags)
                    st.caption(f"자동 태그: {tag_label if tag_label else '없음'}")

        conn = sqlite3.connect(DB_PATH)
        try:
            for rule in extracted.get("rules", []):
                insert_rule(conn, rule)
            for term in extracted.get("terms", []):
                insert_term(conn, term)
            for case in extracted.get("cases", []):
                insert_case(conn, case)
        finally:
            conn.close()


# ------------------------------------------------------------
# 📂 2. 사례 보기 / 삭제 / 검색 / 필터
# ------------------------------------------------------------
with TABS[1]:
    st.header("📂 사례 관리")
    keyword = st.text_input("검색 (제목·요약·태그)", "")
    tag_filter = st.selectbox(
        "카테고리 필터",
        ["전체", "혼인", "직업", "재물", "건강", "기타"],
        index=0,
    )

    cases = fetch_cases(DB_PATH, keyword=keyword, tag_filter=tag_filter)

    if not cases:
        st.info("표시할 사례가 없습니다.")
    else:
        for case in cases:
            tag_text = case.get("tags", "") or "-"
            expander_label = f"📁 {case.get('title', '사례')} ({tag_text})"
            with st.expander(expander_label, expanded=False):
                st.markdown(f"**명조:** {case.get('chart', '-')}")
                st.markdown(f"**요약:** {case.get('summary', '요약 없음')}")
                st.text_area(
                    "본문",
                    case.get("content", ""),
                    height=250,
                    key=f"case_view_{case['id']}",
                )

                related_rules = case.get("related_rules") or []
                related_terms = case.get("related_terms") or []

                if related_rules:
                    st.markdown("**🔗 연결된 규칙**")
                    for title in related_rules:
                        st.write(f"- {title}")

                if related_terms:
                    st.markdown("**📘 연결된 용어**")
                    for term in related_terms:
                        st.write(f"- {term}")

                delete_col, _ = st.columns([1, 4])
                with delete_col:
                    if st.button(
                        f"🗑 삭제 {case['id']}", key=f"delete_case_{case['id']}"
                    ):
                        delete_case(DB_PATH, case["id"])
                        st.warning(f"{case.get('title', '사례')} 삭제됨")
                        st.experimental_rerun()


# ------------------------------------------------------------
# 📘 3. 용어 정리
# ------------------------------------------------------------
with TABS[2]:
    st.header("📘 용어 정리")
    terms = fetch_terms(DB_PATH)
    if terms:
        st.dataframe(terms)
    else:
        st.info("등록된 용어가 없습니다.")


# ------------------------------------------------------------
# 🔍 4. 규칙 보기
# ------------------------------------------------------------
with TABS[3]:
    st.header("🔍 규칙 보기")
    rules = fetch_rules(DB_PATH)
    if rules:
        st.dataframe(rules)
    else:
        st.info("등록된 규칙이 없습니다.")


# ------------------------------------------------------------
# 🌐 5. 시각화
# ------------------------------------------------------------
with TABS[4]:
    st.header("🌐 명조 구조 시각화")
    chart_name = st.text_input("시각화할 명조 이름")
    if st.button("시각화 실행"):
        relations = [("午", "卯", "破"), ("卯", "亥", "合")]
        html_path = draw_chart_relations(chart_name or "chart", relations)
        with open(html_path, "r", encoding="utf-8") as html_file:
            st.components.v1.html(html_file.read(), height=600, scrolling=True)

