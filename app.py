import streamlit as st
import json, os
from merge_rules import merge_rules_to_master
from match_rules import match_rules, load_rules

st.set_page_config(page_title="규칙 분석기", page_icon="🔮", layout="wide")

# 스타일 적용
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1 class='title'>🔮 규칙 분석 대시보드</h1>", unsafe_allow_html=True)

# 탭
tab1, tab2, tab3 = st.tabs(["⚙ 규칙 병합", "📊 규칙 시각화", "🧮 자동 판정"])

# --- 1️⃣ 규칙 병합 ---
with tab1:
    st.header("⚙ 규칙 병합")
    st.info("rules 폴더의 개별 규칙 파일을 병합하여 rules_master.json으로 저장합니다.")
    if st.button("🔄 병합 실행"):
        merged = merge_rules_to_master()
        st.success(f"{len(merged)}개 규칙이 병합되었습니다.")
        st.json(merged)

# --- 2️⃣ 규칙 시각화 ---
with tab2:
    st.header("📊 규칙 시각화")
    try:
        rules = load_rules()
        keyword = st.text_input("검색어 입력 (예: 이혼, 再緣, 爭夫):", "")
        filtered = {k: v for k, v in rules.items() if keyword in json.dumps(v, ensure_ascii=False)}
        st.metric("규칙 수", len(filtered))
        st.json(filtered)
    except FileNotFoundError:
        st.warning("rules_master.json이 없습니다. 먼저 병합을 실행하세요.")

# --- 3️⃣ 자동 판정 ---
with tab3:
    st.header("🧮 새로운 사주 → 규칙 판정")
    c1, c2, c3 = st.columns(3)
    with c1: day_stem = st.text_input("일간(天干):", "辛")
    with c2: branches = st.text_input("지지 (띄어쓰기):", "巳 午 卯 亥").split()
    with c3: relations = st.text_input("주요 관계(쉼표 구분):", "午卯破, 丑午穿").split(",")

    if st.button("🔎 판정 실행"):
        chart = {"day_stem": day_stem, "branches": branches, "relations": relations}
        matched = match_rules(chart)
        applied = [r for r, v in matched.items() if v]
        st.success(f"적용된 규칙 {len(applied)}개")

        for rule_id in applied:
            rule = rules.get(rule_id, {})
            with st.container():
                st.markdown(f"""
                <div class='rule-card'>
                    <h3>{rule_id}</h3>
                    <p><b>결과:</b> {rule.get('result','')}</p>
                    <p><b>원리:</b> {rule.get('principle','')}</p>
                    <p><b>출처:</b> {rule.get('source','')}</p>
                </div>
                """, unsafe_allow_html=True)

        # 간단한 유형 분류
        types = {
            "이혼형": any("이혼" in rules[r]["result"] for r in applied),
            "재혼형": any("재혼" in rules[r]["result"] for r in applied),
            "독신형": any("독신" in rules[r]["result"] for r in applied)
        }
        detected = [k for k, v in types.items() if v]
        if detected:
            st.subheader("🔮 판정 유형")
            st.success(f"→ {' / '.join(detected)} 구조로 분류됨")
        else:
            st.info("특정 혼인 유형에 해당하지 않습니다.")
