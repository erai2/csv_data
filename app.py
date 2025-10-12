import streamlit as st
import json
import os
from merge_rules import merge_rules_to_master
from match_rules import match_rules, load_rules

# --- 페이지 설정 ---
st.set_page_config(page_title="SURI QnA", page_icon="🔮", layout="wide")

# --- 스타일 불러오기 ---
if os.path.exists("assets/style.css"):
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 제목 ---
st.markdown("<h1 class='title'>🔮 SURI QnA Dashboard</h1>", unsafe_allow_html=True)

# --- 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["⚙ 규칙 병합", "📊 규칙 시각화", "🧮 자동 판정"])

# --------------------------------------------------------------------
# ① 규칙 병합 탭
# --------------------------------------------------------------------
with tab1:
    st.header("⚙ 규칙 병합")
    st.info("rules 폴더의 개별 규칙 파일들을 병합하여 rules_master.json으로 저장합니다.")
    
    if st.button("🔄 규칙 병합 실행"):
        merged = merge_rules_to_master()
        st.success(f"{len(merged)}개 규칙이 병합되었습니다.")
        st.json(merged)

# --------------------------------------------------------------------
# ② 규칙 시각화 탭
# --------------------------------------------------------------------
with tab2:
    st.header("📊 규칙 시각화")
    try:
        rules = load_rules()
        keyword = st.text_input("검색어 입력 (예: 이혼, 再緣, 爭夫):", "")
        filtered = {k: v for k, v in rules.items() if keyword in json.dumps(v, ensure_ascii=False)}
        st.metric("검색 결과 수", len(filtered))
        st.json(filtered)
    except FileNotFoundError:
        st.warning("rules_master.json이 없습니다. 먼저 병합을 실행하세요.")

# --------------------------------------------------------------------
# ③ 자동 판정 탭
# --------------------------------------------------------------------
with tab3:
    st.header("🧮 새로운 사주 → 규칙 자동 판정")
    c1, c2, c3 = st.columns(3)
    with c1:
        day_stem = st.text_input("일간(天干):", "辛")
    with c2:
        branches = st.text_input("지지 (띄어쓰기):", "巳 午 卯 亥").split()
    with c3:
        relations = st.text_input("주요 관계 (쉼표로 구분):", "午卯破, 丑午穿").split(",")

    if st.button("🔎 판정 실행"):
        try:
            rules = load_rules()
        except FileNotFoundError:
            st.error("rules_master.json이 없습니다. 먼저 규칙 병합을 실행하세요.")
            st.stop()

        chart = {"day_stem": day_stem, "branches": branches, "relations": relations}
        matched = match_rules(chart)
        applied = [r for r, v in matched.items() if v]

        st.success(f"적용된 규칙 {len(applied)}개")

        # --- 결과 카드 형태로 표시 ---
        for rule_id in applied:
            rule = rules.get(rule_id, {})
            st.markdown(f"""
            <div style="background-color:#f8f9fa;border-left:5px solid #764ba2;
                        padding:12px;margin-bottom:10px;border-radius:8px;">
                <h4>{rule_id}</h4>
                <p><b>결과:</b> {rule.get('result','')}</p>
                <p><b>원리:</b> {rule.get('principle','')}</p>
                <p><b>출처:</b> {rule.get('source','')}</p>
            </div>
            """, unsafe_allow_html=True)

        # --- 유형 분류 ---
        types = {
            "이혼형": any("이혼" in rules[r]["result"] for r in applied if r in rules),
            "재혼형": any("재혼" in rules[r]["result"] for r in applied if r in rules),
            "독신형": any("독신" in rules[r]["result"] for r in applied if r in rules)
        }
        detected = [k for k, v in types.items() if v]

        if detected:
            st.subheader("🔮 판정 유형")
            st.success(f"→ {' / '.join(detected)} 구조로 분류됨")
        else:
            st.info("특정 혼인 유형에 해당하지 않습니다.")
