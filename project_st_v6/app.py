# app.py
import streamlit as st
import os
import json
import re
from universal_parser import parse_documents
from loader import load_parsed_data
from system import SajuAnalyzer, HeavenlyStem, EarthlyBranch, Pillar, Saju
from runner import save_report

# --- 사이드바 메뉴 ---
menu = st.sidebar.radio("메뉴 선택", ["문서 업로드 & 파싱", "분석 실행", "리포트 보기"])

# --- 하이라이트 유틸 ---
def highlight_rules(text, rules):
    """추출된 규칙 키워드를 원문에 하이라이트"""
    highlighted = text
    if not rules:
        return highlighted
    for category, values in rules.items():
        if isinstance(values, list):
            for v in values:
                highlighted = re.sub(
                    v, f"**:red[{v}]**", highlighted
                )
        elif isinstance(values, str):
            highlighted = re.sub(
                values, f"**:red[{values}]**", highlighted
            )
    return highlighted

# --- 1. 문서 업로드 & 파싱 ---
if menu == "문서 업로드 & 파싱":
    st.header("📂 문서 업로드 & 파싱")

    uploaded_files = st.file_uploader("문서 업로드 (txt/md)", type=["txt", "md"], accept_multiple_files=True)

    if uploaded_files:
        os.makedirs("docs", exist_ok=True)
        for file in uploaded_files:
            filepath = os.path.join("docs", file.name)
            with open(filepath, "wb") as f:
                f.write(file.read())
        st.success(f"{len(uploaded_files)}개 문서 저장 완료 ✅")

        # 바로 파싱 실행
        parsed = parse_documents("docs")
        with open("parsed_all.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

        st.subheader("📑 파싱 결과 미리보기")
        st.json(parsed)

        # 업로드된 문서 원문 + 하이라이트 표시
        st.subheader("📄 원문 + 규칙 하이라이트")
        for fname in os.listdir("docs"):
            if fname.endswith((".txt", ".md")):
                with open(os.path.join("docs", fname), "r", encoding="utf-8") as f:
                    content = f.read()
                rules = parsed.get(fname, {})
                st.markdown(f"### {fname}")
                st.markdown(highlight_rules(content, rules))

# --- 2. 분석 실행 ---
elif menu == "분석 실행":
    st.header("🔮 분석 실행")

    if not os.path.exists("parsed_all.json"):
        st.warning("먼저 문서를 업로드 & 파싱해주세요.")
    else:
        parsed_data, shishin_mgr, gungwi_mgr = load_parsed_data("parsed_all.json")

        # 예시 사주
        year = Pillar(HeavenlyStem("丙", "화", "양"), EarthlyBranch("申", "금", "양", {"경": {"ohaeng": "금", "yinyang": "양"}}))
        month = Pillar(HeavenlyStem("丙", "화", "양"), EarthlyBranch("申", "금", "양", {"경": {"ohaeng": "금", "yinyang": "양"}}))
        day = Pillar(HeavenlyStem("辛", "금", "음"), EarthlyBranch("酉", "금", "음", {"신": {"ohaeng": "금", "yinyang": "음"}}))
        time = Pillar(HeavenlyStem("丁", "화", "음"), EarthlyBranch("未", "토", "음", {"기": {"ohaeng": "토", "yinyang": "음"}}))

        saju = Saju(year, month, day, time, gungwi_mgr)
        analyzer = SajuAnalyzer(saju, shishin_mgr, parsed_data)

        st.write("### 사주 구성")
        st.text(str(saju))

        st.write("### [궁위 분석]")
        st.text(analyzer.analyze_gungwi())

        st.write("### [십신 분석]")
        st.text(analyzer.analyze_sipsin())

        st.write("### [지지 관계 분석]")
        st.text(analyzer.analyze_branch_relations())

        st.write("### [고급 규칙 분석]")
        st.text(analyzer.analyze_advanced_rules())

        # 보고서 저장
        report_text = "\n".join([
            "=== 분석 리포트 ===",
            str(saju),
            "\n[궁위]", analyzer.analyze_gungwi(),
            "\n[십신]", analyzer.analyze_sipsin(),
            "\n[지지 관계]", analyzer.analyze_branch_relations(),
            "\n[고급 규칙]", analyzer.analyze_advanced_rules()
        ])
        save_report(report_text, "streamlit_report")
        st.success("리포트 저장 완료 ✅")

# --- 3. 리포트 보기 ---
elif menu == "리포트 보기":
    st.header("📑 저장된 리포트")

    for fmt in ["md", "json", "pdf"]:
        path = f"reports/streamlit_report.{fmt}"
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(
                    label=f"{fmt.upper()} 다운로드",
                    data=f.read(),
                    file_name=f"streamlit_report.{fmt}"
                )
