import streamlit as st
import pandas as pd

# -------------------------------
# ⚙️ 계산 함수 정의
# -------------------------------
def calc_kongmang(day_pillar):
    table = {
        "戊辰": "寅卯", "己巳": "子丑", "庚午": "戌亥", "辛未": "申酉",
        "壬申": "午未", "癸酉": "辰巳", "甲戌": "寅卯", "乙亥": "子丑"
    }
    return table.get(day_pillar, "해당 없음")

def calc_jeap(relations):
    if "沖" in relations or "破" in relations:
        return "충파제압"
    elif "合" in relations:
        return "합화제압"
    elif "刑" in relations:
        return "형극제압"
    else:
        return "일반제압"

def calc_daeun(stem, branch):
    stems = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    branches = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    i, j = stems.index(stem), branches.index(branch)
    daeun = [f"{stems[(i+k)%10]}{branches[(j+k)%12]}" for k in range(8)]
    return " → ".join(daeun)

def interpret_category(category, gender, pillar_day):
    # 간단한 자동 해석 구조 예시
    if category == "혼인":
        if "午" in pillar_day or "卯" in pillar_day:
            return "夫星이 夫宮에 들어 혼인 성립, 午卯破 시 이혼 가능성"
        else:
            return "夫宮 안정, 현실혼 가능"
    elif category == "직업":
        if "辛" in pillar_day or "巳" in pillar_day:
            return "食神生財格, 문화·언론계 직업 유리"
        else:
            return "官印相生格, 행정·교육계 적합"
    elif category == "재물":
        if "財" in pillar_day or "巳" in pillar_day:
            return "財庫開, 발재운"
        else:
            return "재성 약, 절약형"
    elif category == "건강":
        if "水" in pillar_day or "酉" in pillar_day:
            return "신장·혈압 유의"
        else:
            return "체력 안정"
    elif category == "육친":
        return "부모: 印, 배우자: 官, 자녀: 食傷 중심으로 안정"
    return "분석 데이터 없음"


# -------------------------------
# 🧭 Streamlit UI 시작
# -------------------------------
st.set_page_config(page_title="자동 해석 시스템 v4", layout="wide")
st.title("🔮 v4")

tabs = st.tabs(["🧭 기본 구조", "💍 혼인 분석", "💼 직업·재물", "🧠 건강·육친"])

# -------------------------------
# 🧭 ① 기본 구조 탭
# -------------------------------
with tabs[0]:
    st.subheader("📘 사주 구성 (천간/지지 2행 구조)")

    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("성별", ["乾(남)", "坤(여)"])
        saju = st.text_input("사주 8자 입력 (예: 戊辰 辛酉 己巳 乙丑)", "戊辰 辛酉 己巳 乙丑")
    with col2:
        relation = st.text_input("주요 관계 (합·충·형·파)", "巳酉丑, 午卯破")

    if st.button("🔍 분석 실행", key="main_analysis"):
        pillars = saju.split()
        if len(pillars) != 4:
            st.error("사주 4기둥(8자)을 올바르게 입력하세요.")
            st.stop()

        pillars = pillars[::-1]  # 時-日-月-年 순
        stems = [p[0] for p in pillars]
        branches = [p[1] for p in pillars]

        kongmang = calc_kongmang(pillars[1])
        jeap = calc_jeap(relation)
        daeun = calc_daeun(pillars[1][0], pillars[1][1])

        df1 = pd.DataFrame({
            "구분": ["天干", "地支"],
            "時柱": [stems[0], branches[0]],
            "日柱": [stems[1], branches[1]],
            "月柱": [stems[2], branches[2]],
            "年柱": [stems[3], branches[3]]
        })

        summary = pd.DataFrame([
            ["성별", gender],
            ["공망", kongmang],
            ["제압수단", jeap],
            ["대운", daeun],
            ["운세 해석", "財統官格 / 食神生財格 / 안정된 혼인"]
        ], columns=["항목", "내용"])

        st.table(df1)
        st.table(summary)

# -------------------------------
# 💍 ② 혼인 분석 탭
# -------------------------------
with tabs[1]:
    st.subheader("💍 혼인/배우자 해석")
    saju = st.text_input("사주 입력 (예: 戊辰 辛酉 己巳 乙丑)", key="marriage")
    if st.button("혼인 해석", key="marriage_btn"):
        if saju:
            result = interpret_category("혼인", "坤", saju)
            st.success(f"🔹 해석 결과: {result}")
        else:
            st.warning("사주를 입력하세요.")

# -------------------------------
# 💼 ③ 직업/재물 탭
# -------------------------------
with tabs[2]:
    st.subheader("💼 직업 및 재물 해석")
    saju = st.text_input("사주 입력", key="career")
    if st.button("직업 해석", key="career_btn"):
        job = interpret_category("직업", "乾", saju)
        money = interpret_category("재물", "乾", saju)
        st.info(f"💼 직업: {job}")
        st.success(f"💰 재물: {money}")

# -------------------------------
# 🧠 ④ 건강/육친 탭
# -------------------------------
with tabs[3]:
    st.subheader("🧠 건강 및 육친 해석")
    saju = st.text_input("사주 입력", key="health")
    if st.button("건강/육친 해석", key="health_btn"):
        health = interpret_category("건강", "乾", saju)
        family = interpret_category("육친", "乾", saju)
        st.info(f"🧘 건강: {health}")
        st.success(f"👨‍👩‍👧 육친: {family}")

# -------------------------------
# 🪶 푸터
# -------------------------------
st.markdown("""
---
** 자동 해석 시스템 v4**
- 구조 해석: 合/沖/刑/破/穿/入墓 기반  
- 운세 해석: 財統官格 / 官印相生格 / 食神生財格  
- Version 4 © Suri Platform
""")
