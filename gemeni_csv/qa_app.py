import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
import os
import json
import pandas as pd
import re
import shutil
# 로컬 유틸리티 파일 임포트
import data_utils

# --- 설정 ---
DATA_DIRECTORY = "data"
DB_DIRECTORY = "chroma_db"
JSON_FILE_PATH = "knowledge_base.json"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL_REPO_ID = "google/gemma-2-9b-it" 

# --- AI Q&A 및 LLM 관련 함수 ---
@st.cache_resource
def load_vector_db():
    if not os.path.exists(DB_DIRECTORY): return None
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(persist_directory=DB_DIRECTORY, embedding_function=embeddings)

@st.cache_resource
def get_llm(hf_api_token):
    if not hf_api_token: return None
    try:
        return HuggingFaceEndpoint(
            repo_id=LLM_MODEL_REPO_ID, huggingfacehub_api_token=hf_api_token,
            temperature=0.1, max_new_tokens=2048
        )
    except Exception as e:
        st.error(f"LLM 로드 중 오류: {e}")
        return None

def create_qa_chain(vector_db, llm):
    if not llm: return None
    retriever = vector_db.as_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

# --- Streamlit UI ---
st.set_page_config(page_title="AI 시스템", layout="wide")
st.title("🔮 AI 통합 시스템")

# --- 사이드바 ---
st.sidebar.header("API 설정")
hf_token = st.sidebar.text_input("Hugging Face API 토큰", type="password")

st.sidebar.divider()
st.sidebar.header("📂 데이터 관리")
uploaded_files = st.sidebar.file_uploader(
    "지식 파일(.md, .txt) 업로드",
    type=["md", "txt"],
    accept_multiple_files=True
)
if uploaded_files:
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
    file_names = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DATA_DIRECTORY, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_names.append(uploaded_file.name)
    st.sidebar.success(f"{len(file_names)}개 파일 저장 완료: {', '.join(file_names)}")

st.sidebar.divider()
st.sidebar.header("⚙️ DB 관리")
if st.sidebar.button("데이터베이스 재생성"):
    if not os.path.exists(DATA_DIRECTORY) or not os.listdir(DATA_DIRECTORY):
        st.sidebar.error(f"'{DATA_DIRECTORY}' 폴더가 비어있습니다. 먼저 파일을 업로드해주세요.")
    else:
        if os.path.exists(DB_DIRECTORY):
            shutil.rmtree(DB_DIRECTORY)
        status = st.sidebar.empty()
        with st.spinner("데이터 처리 및 DB 생성 중..."):
            data_utils.process_and_embed(DATA_DIRECTORY, status)
        st.rerun()

# --- 메인 화면 탭 ---
tab1, tab2 = st.tabs(["🤖 AI Q&A", "📚 지식 베이스 탐색기"])

with tab1:
    st.header("AI에게 질문하기")
    db = load_vector_db()
    if not db:
        st.info("사이드바에서 지식 파일을 업로드한 후 '데이터베이스 재생성' 버튼을 클릭하여 DB를 생성해주세요.")
    else:
        llm = get_llm(hf_token)
        qa_chain = create_qa_chain(db, llm)
        query = st.text_input("질문을 입력하세요:", placeholder="예: 제압수단의 종류와 각각의 작용을 알려주세요.", key="qa_query")
        if query and qa_chain:
            with st.spinner("AI가 답변을 생성하는 중입니다..."):
                result = qa_chain.invoke(query)
                st.subheader("AI 답변")
                st.write(result["result"])
                with st.expander("📚 답변 근거 (AI가 참조한 문서)"):
                    for doc in result["source_documents"]:
                        st.markdown(f"**- 제목: {doc.metadata.get('title', 'N/A')}**")
                        st.caption(f"내용: {doc.page_content}")
with tab2:
    st.header("지식 베이스 탐색기 (knowledge_base.json)")
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        df = pd.DataFrame(full_data)
        st.dataframe(df, use_container_width=True)
    except FileNotFoundError:
        st.info(f"'{JSON_FILE_PATH}' 파일이 없습니다. 사이드바에서 파일을 업로드하고 '데이터베이스 재생성'을 실행해주세요.")

