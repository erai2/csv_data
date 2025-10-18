"""Streamlit expert interface for the Suam Myeongri knowledge base."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="전문가 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_data(file_path: Path) -> Dict[str, Any] | None:
    """Load JSON payload from disk."""
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_term_details(term: Dict[str, Any]) -> None:
    """Render additional metadata for a term inside an expander."""
    detail_keys: List[str] = [
        key
        for key in term.keys()
        if key not in {"name", "definition", "description", "category"}
    ]
    if not detail_keys:
        st.caption("추가 속성이 없습니다.")
        return

    num_columns = max(1, len(detail_keys))
    columns = st.columns(num_columns)

    for index, key in enumerate(detail_keys):
        with columns[index % num_columns]:
            st.markdown(f"**{key}**")
            value = term[key]
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    st.markdown(f"- **{sub_key}**: {sub_value}")
            elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                for item in value:
                    st.markdown(f"- {item}")
            else:
                st.markdown(str(value))


# --- 데이터 로드 ---
DATA_FILE = Path(__file__).with_name("suam_master_data.json")

data: Dict[str, Any] | None = None
if DATA_FILE.exists():
    try:
        data = load_data(DATA_FILE)
    except json.JSONDecodeError as exc:  # pragma: no cover - UI feedback
        st.error(f"데이터 파일 파싱 실패: {exc}")
else:
    template_path = (Path(__file__).parent / "data" / "templates" / "suam_master_data.template.json").resolve()
    st.warning(
        "`suam_master_data.json` 파일이 존재하지 않습니다.\n"
        "템플릿을 복사하여 데이터를 준비한 뒤 다시 실행하세요.\n"
        f"템플릿 경로: `{template_path}`"
    )

if data is None:
    st.stop()


# --- 사이드바 UI ---
with st.sidebar:
    st.title("📚 수암명리 매뉴얼")
    st.caption("v2.0 전문가 에디션")
    st.markdown("---")

    page_options = [
        "🏠 홈",
        "📖 용어 사전",
        "⚛️ 구조론 (합충형파)",
        "🌟 주제별 분석",
        "💡 심화 개념",
        "📂 사례 연구",
    ]
    selected_page = st.radio("메뉴 선택", page_options, label_visibility="visible")

    st.markdown("---")
    st.info("통합된 명리학 지식 베이스를 탐색하세요.")


# --- 페이지별 콘텐츠 구현 ---
if selected_page == "🏠 홈":
    st.title("수암명리 전문가 시스템")
    st.markdown("---")
    st.markdown(
        """
        **수암명리 매뉴얼의 핵심 이론과 실제 사례를 통합한 전문가용 지식 플랫폼입니다.**

        👈 왼쪽 메뉴를 통해 명리학의 방대한 세계를 체계적으로 탐색해 보세요.
        이 시스템은 다양한 원문 자료를 기반으로 구축되어, 깊이 있는 학습과 실전 응용을 지원합니다.
        """
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 주요 기능")
        st.success("- **통합 용어 사전**: 핵심 용어를 빠르게 검색하고 심성, 상(象), 조건을 한눈에 파악합니다.")
        st.success("- **구조론**: 합, 충, 형, 파 등 사주 구조를 결정하는 핵심 작용을 심도 있게 분석합니다.")
        st.success("- **주제별 분석**: 연애, 직업, 재물 등 현대적 관심사에 대한 명리학적 접근법을 제시합니다.")
    with col2:
        st.subheader("💡 심화 학습")
        st.info("- **심화 개념**: 허투(虛透), 대상(帶象), 활목/사목(活木/死木) 등 고급 이론을 상세히 다룹니다.")
        st.info("- **사례 연구**: 실제 팔자를 기반으로 한 다양한 사례를 통해 이론의 실전 적용 능력을 배양합니다.")

elif selected_page == "📖 용어 사전":
    st.title("📖 용어 사전")
    terms: List[Dict[str, Any]] = data.get("terms", [])
    if not terms:
        st.info("등록된 용어가 없습니다.")
    else:
        search_query = st.text_input("검색할 용어를 입력하세요 (예: 록신, 허투, 대상)")
        lowered = search_query.lower().strip()
        results = [term for term in terms if lowered in term["name"].lower()] if lowered else terms

        if not results:
            st.warning("검색 결과가 없습니다.")
        else:
            for term in sorted(results, key=lambda item: item["name"]):
                with st.expander(f"**{term['name']}** - {term['definition']}"):
                    if term.get("description"):
                        st.write(term["description"])
                    render_term_details(term)

elif selected_page == "⚛️ 구조론 (합충형파)":
    structural = data.get("structural_concepts")
    if not structural:
        st.info("구조론 데이터가 없습니다.")
    else:
        st.title(f"⚛️ {structural.get('title', '구조론')}")
        items: List[Dict[str, Any]] = structural.get("items", [])
        if not items:
            st.info("구조론 항목이 없습니다.")
        else:
            tabs = st.tabs([item.get("name", "항목") for item in items])
            for index, item in enumerate(items):
                with tabs[index]:
                    name = item.get("name", "항목")
                    definition = item.get("definition", "정의 없음")
                    st.subheader(f"{name} - {definition}")
                    st.markdown("##### **해석 방식**")
                    st.info(item.get("interpretation", "-") or "-")
                    st.markdown("##### **관련 키워드**")
                    keywords = item.get("keywords") or []
                    if keywords:
                        st.write(", ".join(str(keyword) for keyword in keywords))
                    else:
                        st.write("키워드 정보 없음")

elif selected_page == "🌟 주제별 분석":
    thematic = data.get("thematic_analysis")
    if not thematic:
        st.info("주제별 분석 데이터가 없습니다.")
    else:
        st.title(f"🌟 {thematic.get('title', '주제별 분석')}")
        items = thematic.get("items", [])
        if not items:
            st.info("등록된 분석 항목이 없습니다.")
        else:
            theme_name = st.selectbox("분석할 주제를 선택하세요.", [item.get("name", "항목") for item in items])
            selected_theme = next((item for item in items if item.get("name") == theme_name), None)
            if selected_theme:
                st.subheader(selected_theme.get("name", "항목"))
                if selected_theme.get("description"):
                    st.markdown(selected_theme["description"])
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    palaces = selected_theme.get("palace") or []
                    st.info(f"**주요 궁위(宮位)**: {', '.join(palaces) if palaces else '-'}")
                with col2:
                    stars = selected_theme.get("star") or []
                    st.success(f"**핵심 성(星)**: {', '.join(stars) if stars else '-'}")
                with col3:
                    triggers = selected_theme.get("trigger") or []
                    st.warning(f"**작용(Trigger)**: {', '.join(triggers) if triggers else '-'}")

elif selected_page == "💡 심화 개념":
    st.title("💡 심화 개념 해설")
    advanced_terms = [term for term in data.get("terms", []) if term.get("category") == "심화 개념"]
    if not advanced_terms:
        st.info("심화 개념 데이터가 없습니다.")
    else:
        for term in advanced_terms:
            with st.expander(f"**{term['name']}** - {term['definition']}"):
                if term.get("description"):
                    st.write(term["description"])
                details = term.get("details")
                if details:
                    for key, value in details.items():
                        st.markdown(f"- **{key}**: {value}")

elif selected_page == "📂 사례 연구":
    st.title("📂 사례 연구")
    cases = data.get("cases") or []
    if not cases:
        st.info("사례 데이터가 없습니다.")
    else:
        df = pd.DataFrame(cases)
        if df.empty:
            st.info("표시할 사례가 없습니다.")
        else:
            unique_gyeokguk = sorted(df["gyeokguk"].dropna().unique())
            selected_gyeokguk = st.multiselect(
                "격국(格局)으로 필터링:", options=unique_gyeokguk, default=unique_gyeokguk
            )
            if selected_gyeokguk:
                filtered_df = df[df["gyeokguk"].isin(selected_gyeokguk)]
            else:
                filtered_df = df

            st.dataframe(filtered_df, use_container_width=True)

            if not filtered_df.empty:
                st.markdown("---")
                st.subheader("사례 상세 분석")
                selected_id = st.selectbox("분석할 사례 ID를 선택하세요.", options=filtered_df["id"].tolist())
                if selected_id:
                    case_details = filtered_df[filtered_df["id"] == selected_id].iloc[0]
                    st.info(f"**팔자:** {case_details.get('chart', '-')}")
                    st.write(f"**분석:** {case_details.get('analysis', '분석 정보 없음')}")

# 데이터 로드 실패 시 이미 st.stop() 호출로 종료됨
