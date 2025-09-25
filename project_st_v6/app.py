# app.py
import streamlit as st,os,json
from universal_parser import parse_documents
from runner import run_analysis
from merge_reports import merge_reports

st.set_page_config(page_title="Suri Project",layout="wide")
st.title("🔮 Suri_v6")

tab1,tab2,tab3=st.tabs(["📂parsing","📊 analyzer","📑 report"])

with tab1:
    st.header("문서 업로드 및 파싱")
    files=st.file_uploader("문서 업로드",type=["txt","md"],accept_multiple_files=True)
    if st.button("파싱 실행"):
        os.makedirs("docs",exist_ok=True)
        for f in files:
            path=os.path.join("docs",f.name)
            with open(path,"wb") as out: out.write(f.read())
        parsed=parse_documents("docs")
        st.json(parsed)
        st.success("✅ parsed_all.json 생성")

with tab2:
    st.header("분석")
    if st.button("분석 실행"):
        text=run_analysis()
        st.text_area("분석 결과",text,height=400)
        st.success("보고서 저장 완료")

with tab3:
    st.header("보고서 병합")
    if st.button("병합 실행"):
        out=merge_reports()
        st.success(f"📑 병합 보고서: {out}")
