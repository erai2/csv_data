"""Streamlit entry point for the explainable fortune inference system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import streamlit as st

from utils import extractor_v4
from utils.db_manager import (
    init_db,
    list_principles,
    list_relations,
    list_rules,
    record_principles,
    record_relations,
    record_rules,
    search_relations,
    search_rules,
)
from utils.logic_infer_explainable import infer_logic_explainable
from utils.profile_manager import delete_profile, list_profiles, load_profile, save_profile
from utils.saju_core_v2 import EARTHLY_BRANCHES, HEAVENLY_STEMS, analyze_saju
from utils.visualize_v3 import draw_relation_network


st.set_page_config(page_title="AI 명리 해석 시스템 v13.2", layout="wide")
st.title("🪶 AI 명리 해석 시스템 (Explainable Ver.)")


# ---------------------------------------------------------------------------
# Initial session state
# ---------------------------------------------------------------------------
DEFAULT_GAN = ["丁", "戊", "辛", "辛"]
DEFAULT_ZHI = ["午", "卯", "亥", "子"]

GAN_KEYS = ["gan_si", "gan_il", "gan_wol", "gan_nyeon"]
ZHI_KEYS = ["zhi_si", "zhi_il", "zhi_wol", "zhi_nyeon"]


def _ensure_session_defaults() -> None:
    for key, value in zip(GAN_KEYS, DEFAULT_GAN):
        st.session_state.setdefault(key, value)
    for key, value in zip(ZHI_KEYS, DEFAULT_ZHI):
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("gan_input", " ".join(DEFAULT_GAN))
    st.session_state.setdefault("zhi_input", " ".join(DEFAULT_ZHI))
    st.session_state.setdefault("daewoon", "甲午")
    st.session_state.setdefault("sewoon", "乙亥")
    st.session_state.setdefault("profile_to_load", "새 프로필")
    st.session_state.setdefault("latest_structure", None)
    st.session_state.setdefault("latest_results", None)
    st.session_state.setdefault("latest_profile_name", "analysis")


def _sync_gan_from_selects() -> None:
    st.session_state["gan_input"] = " ".join(st.session_state[key] for key in GAN_KEYS)


def _sync_zhi_from_selects() -> None:
    st.session_state["zhi_input"] = " ".join(st.session_state[key] for key in ZHI_KEYS)


def _sync_selects_from_gan() -> None:
    parts = st.session_state.get("gan_input", "").split()
    for idx, key in enumerate(GAN_KEYS):
        if idx < len(parts) and parts[idx] in HEAVENLY_STEMS:
            st.session_state[key] = parts[idx]


def _sync_selects_from_zhi() -> None:
    parts = st.session_state.get("zhi_input", "").split()
    for idx, key in enumerate(ZHI_KEYS):
        if idx < len(parts) and parts[idx] in EARTHLY_BRANCHES:
            st.session_state[key] = parts[idx]


_ensure_session_defaults()


# ---------------------------------------------------------------------------
# Database bootstrapping
# ---------------------------------------------------------------------------
init_db()


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _save_uploaded_file(uploaded_file) -> Path:
    uploads_dir = Path("data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / uploaded_file.name
    with open(file_path, "wb") as buffer:
        buffer.write(uploaded_file.read())
    return file_path


def _convert_terms_to_principles(terms: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": term.get("term", ""), "definition": term.get("definition", ""), "category": term.get("category", "용어")}
        for term in terms
    ]


def _cases_to_relations(cases: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    payload: List[Dict[str, str]] = []
    for case in cases:
        tags = case.get("tags", [])
        for tag in tags or ["기타"]:
            payload.append(
                {
                    "relation_type": tag,
                    "description": case.get("summary", ""),
                    "source": case.get("title", "case"),
                }
            )
    return payload


def _structure_relations_to_edges(relations: Sequence[str]) -> List[Tuple[str, str, str]]:
    edges: List[Tuple[str, str, str]] = []
    for relation in relations:
        if len(relation) >= 3:
            source, target, rel_type = relation[0], relation[1], relation[2:]
            if source in EARTHLY_BRANCHES and target in EARTHLY_BRANCHES:
                edges.append((source, target, rel_type))
    return edges


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
tabs = st.tabs(
    [
        "📄 문서 정리/시각화",
        "🪶 사주 명조 및 운세 해석",
        "👤 프로필 관리",
        "🌐 시각화",
        "📘 리포트",
    ]
)


# ---------------------------------------------------------------------------
# Tab 1: 문서 정리/시각화
# ---------------------------------------------------------------------------
with tabs[0]:
    st.header("📄 문서 업로드 및 지식 정리")
    uploaded = st.file_uploader("문서를 업로드하세요", type=["txt", "docx", "pdf", "zip"])

    if uploaded is not None:
        saved_path = _save_uploaded_file(uploaded)
        extracted = extractor_v4.extract_rules_terms_cases(str(saved_path))

        rules = extracted.get("rules", [])
        terms = extracted.get("terms", [])
        cases = extracted.get("cases", [])

        record_rules(rules)
        record_principles(_convert_terms_to_principles(terms))
        record_relations(_cases_to_relations(cases))

        st.success(
            "📦 저장 완료 — 규칙 {rules_count}건, 용어 {terms_count}건, 사례 {cases_count}건".format(
                rules_count=len(rules),
                terms_count=len(terms),
                cases_count=len(cases),
            )
        )

        with st.expander("🧾 추출 요약", expanded=True):
            st.subheader("규칙")
            st.dataframe(rules or [{"condition": "-", "result": "-"}])
            st.subheader("용어/원리")
            st.dataframe(terms or [{"term": "-", "definition": "-"}])
            st.subheader("사례")
            for case in cases:
                with st.expander(f"📁 {case.get('title', '사례')}" ):
                    st.markdown(f"**요약:** {case.get('summary', '요약 없음')}")
                    st.caption(f"태그: {', '.join(case.get('tags', []))}")
                    st.text_area("본문", case.get("content", ""), height=220)

    st.markdown("---")
    st.subheader("🔍 규칙 / 관계 검색")
    col_search_rule, col_search_relation = st.columns(2)
    with col_search_rule:
        keyword = st.text_input("규칙 검색어", "")
        if keyword:
            st.dataframe(search_rules(keyword))
        else:
            st.dataframe(list_rules(limit=20))
    with col_search_relation:
        relation_keyword = st.text_input("관계 검색어", "")
        if relation_keyword:
            st.dataframe(search_relations(relation_keyword))
        else:
            st.dataframe(list_relations(limit=20))


# ---------------------------------------------------------------------------
# Tab 2: 사주 명조 및 운세 해석
# ---------------------------------------------------------------------------
with tabs[1]:
    st.header("🪶 사주 명조 및 운세 해석")

    profiles = list_profiles()
    options = {"새 프로필": None}
    options.update({f"{p['name']} (#{p['id']})": p["id"] for p in profiles})
    selected_option = st.selectbox("저장된 프로필 불러오기", list(options.keys()), key="profile_to_load")

    if selected_option != "새 프로필":
        selected_profile = load_profile(options[selected_option])
    else:
        selected_profile = None

    if selected_profile is not None and st.button("프로필 값 불러오기"):
        gan_values = selected_profile["gan"].split()
        zhi_values = selected_profile["zhi"].split()
        for idx, key in enumerate(GAN_KEYS):
            if idx < len(gan_values) and gan_values[idx] in HEAVENLY_STEMS:
                st.session_state[key] = gan_values[idx]
        for idx, key in enumerate(ZHI_KEYS):
            if idx < len(zhi_values) and zhi_values[idx] in EARTHLY_BRANCHES:
                st.session_state[key] = zhi_values[idx]
        st.session_state["gan_input"] = selected_profile["gan"]
        st.session_state["zhi_input"] = selected_profile["zhi"]
        st.session_state["daewoon"] = selected_profile["daewoon"]
        st.session_state["sewoon"] = selected_profile["sewoon"]
        st.session_state["latest_structure"] = selected_profile["structure"]
        st.session_state["latest_results"] = selected_profile["results"]
        st.session_state["latest_profile_name"] = selected_profile["name"]
        st.experimental_rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("이름", value=selected_profile["name"] if selected_profile else "")
        gender = st.selectbox("성별", ["坤(여)", "乾(남)"], index=0 if not selected_profile or selected_profile["gender"] == "坤(여)" else 1)
    with col2:
        st.markdown("**천간 선택 (시·일·월·년)**")
        st.selectbox("시주 천간", HEAVENLY_STEMS, key="gan_si", on_change=_sync_gan_from_selects)
        st.selectbox("일주 천간", HEAVENLY_STEMS, key="gan_il", on_change=_sync_gan_from_selects)
        st.selectbox("월주 천간", HEAVENLY_STEMS, key="gan_wol", on_change=_sync_gan_from_selects)
        st.selectbox("년주 천간", HEAVENLY_STEMS, key="gan_nyeon", on_change=_sync_gan_from_selects)
    with col3:
        st.markdown("**지지 선택 (시·일·월·년)**")
        st.selectbox("시주 지지", EARTHLY_BRANCHES, key="zhi_si", on_change=_sync_zhi_from_selects)
        st.selectbox("일주 지지", EARTHLY_BRANCHES, key="zhi_il", on_change=_sync_zhi_from_selects)
        st.selectbox("월주 지지", EARTHLY_BRANCHES, key="zhi_wol", on_change=_sync_zhi_from_selects)
        st.selectbox("년주 지지", EARTHLY_BRANCHES, key="zhi_nyeon", on_change=_sync_zhi_from_selects)

    st.markdown("---")
    st.markdown("### ✏️ 직접 입력 (원하면 수정 가능)")
    st.text_input("천간 입력 (시 일 월 년 순)", key="gan_input", on_change=_sync_selects_from_gan)
    st.text_input("지지 입력 (시 일 월 년 순)", key="zhi_input", on_change=_sync_selects_from_zhi)

    col_daewoon, col_sewoon = st.columns(2)
    with col_daewoon:
        st.text_input("대운", key="daewoon")
    with col_sewoon:
        st.text_input("세운", key="sewoon")

    if st.button("🔍 해석 실행"):
        gan_values = st.session_state["gan_input"].split()
        zhi_values = st.session_state["zhi_input"].split()
        structure = analyze_saju(gan_values, zhi_values, gender)
        results = infer_logic_explainable(structure, st.session_state["daewoon"], st.session_state["sewoon"])

        st.session_state["latest_structure"] = structure
        st.session_state["latest_results"] = results
        st.session_state["latest_profile_name"] = name or "analysis"

        st.subheader("🌿 원국 구조")
        st.json(structure)

        st.subheader("🧠 해석 결과 (원리 포함)")
        for result in results:
            with st.expander(f"📂 {result['분야']} — {result['결과']}"):
                st.markdown(f"**근거:** {result['근거']}")
                st.markdown(f"**해석 원리:** {result['원리']}")

        save_profile(
            name or "무명",
            gender,
            st.session_state["gan_input"],
            st.session_state["zhi_input"],
            st.session_state["daewoon"],
            st.session_state["sewoon"],
            structure,
            results,
        )
        st.success(f"✅ 프로필 [{name or '무명'}] 저장 완료")


# ---------------------------------------------------------------------------
# Tab 3: 프로필 관리
# ---------------------------------------------------------------------------
with tabs[2]:
    st.header("👤 프로필 관리")
    profiles = list_profiles()

    if not profiles:
        st.info("저장된 프로필이 없습니다.")
    else:
        for profile in profiles:
            with st.expander(f"🪶 {profile['name']} ({profile['gender']})"):
                st.markdown(f"**대운:** {profile['daewoon']} / **세운:** {profile['sewoon']}")
                st.markdown(f"**명조:** {profile['gan']} | {profile['zhi']}")
                structure = json.loads(profile["structure_json"])
                results = json.loads(profile["result_json"])
                st.json(structure)
                for result in results:
                    st.markdown(f"- {result['분야']}: {result['결과']}")
                if st.button(f"삭제_{profile['id']}", key=f"delete_profile_{profile['id']}"):
                    delete_profile(profile["id"])
                    st.warning(f"{profile['name']} 프로필 삭제됨")
                    st.experimental_rerun()


# ---------------------------------------------------------------------------
# Tab 4: 시각화
# ---------------------------------------------------------------------------
with tabs[3]:
    st.header("🌐 명조 구조 시각화")
    latest_structure = st.session_state.get("latest_structure")

    if latest_structure:
        st.markdown("#### 최신 해석 기반 관계망")
        edges = _structure_relations_to_edges(latest_structure.get("관계", []))
        if edges:
            html_path = draw_relation_network(st.session_state.get("latest_profile_name", "analysis"), edges)
            with open(html_path, "r", encoding="utf-8") as html_file:
                st.components.v1.html(html_file.read(), height=620, scrolling=True)
        else:
            st.info("표시할 관계가 없습니다.")
    else:
        st.info("먼저 해석을 실행하면 관계망을 확인할 수 있습니다.")

    st.markdown("---")
    st.subheader("🛠 수동 관계 입력")
    st.caption("한 줄에 `지지1 지지2 관계유형` 형식으로 입력하세요. 예) `午 卯 破`")
    manual_relations = st.text_area("관계 목록", "")
    if st.button("수동 시각화 실행"):
        edges: List[Tuple[str, str, str]] = []
        for line in manual_relations.splitlines():
            parts = line.strip().split()
            if len(parts) >= 3:
                edges.append((parts[0], parts[1], " ".join(parts[2:])))
        if edges:
            html_path = draw_relation_network("manual", edges)
            with open(html_path, "r", encoding="utf-8") as html_file:
                st.components.v1.html(html_file.read(), height=620, scrolling=True)
        else:
            st.warning("유효한 관계가 없습니다.")


# ---------------------------------------------------------------------------
# Tab 5: 리포트
# ---------------------------------------------------------------------------
with tabs[4]:
    st.header("📘 리포트")
    st.subheader("📚 저장된 원리/규칙 요약")
    principles = list_principles(limit=200)
    rules = list_rules(limit=200)
    st.markdown(f"- 원리 정의: {len(principles)}건")
    st.markdown(f"- 규칙: {len(rules)}건")

    col_principles, col_rules = st.columns(2)
    with col_principles:
        st.dataframe(principles)
    with col_rules:
        st.dataframe(rules)

    st.markdown("---")
    st.subheader("🗂 프로필 리포트")
    profiles = list_profiles()
    if not profiles:
        st.info("다운로드할 프로필이 없습니다.")
    else:
        profile_options = {f"{p['name']} (#{p['id']})": p for p in profiles}
        selected = st.selectbox("리포트로 확인할 프로필", list(profile_options.keys()))
        profile_payload = profile_options[selected]
        payload = {
            "name": profile_payload["name"],
            "gender": profile_payload["gender"],
            "gan": profile_payload["gan"],
            "zhi": profile_payload["zhi"],
            "daewoon": profile_payload["daewoon"],
            "sewoon": profile_payload["sewoon"],
            "structure": json.loads(profile_payload["structure_json"]),
            "results": json.loads(profile_payload["result_json"]),
        }
        st.json(payload)
        st.download_button(
            label="JSON 다운로드",
            data=json.dumps(payload, ensure_ascii=False, indent=2),
            file_name=f"profile_{profile_payload['id']}.json",
            mime="application/json",
        )

