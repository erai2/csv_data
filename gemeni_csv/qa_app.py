import io
import os
import json
import re
import shutil
from pathlib import Path

import pandas as pd
import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
# 로컬 유틸리티 파일 임포트
import data_utils

# --- 설정 ---
APP_ROOT = Path(__file__).resolve().parent
DATA_DIRECTORY = APP_ROOT / "data"
DB_DIRECTORY = data_utils.DB_DIRECTORY
JSON_FILE_PATH = data_utils.JSON_FILE_PATH
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
    if not DATA_DIRECTORY.exists():
        DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_names = []
    for uploaded_file in uploaded_files:
        file_path = DATA_DIRECTORY / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_names.append(uploaded_file.name)
    st.sidebar.success(f"{len(file_names)}개 파일 저장 완료: {', '.join(file_names)}")

st.sidebar.divider()
st.sidebar.header("⚙️ DB 관리")
if st.sidebar.button("데이터베이스 재생성"):
    if not DATA_DIRECTORY.exists() or not any(DATA_DIRECTORY.iterdir()):
        st.sidebar.error(f"'{DATA_DIRECTORY}' 폴더가 비어있습니다. 먼저 파일을 업로드해주세요.")
    else:
        if os.path.exists(DB_DIRECTORY):
            shutil.rmtree(DB_DIRECTORY)
        status = st.sidebar.empty()
        with st.spinner("데이터 처리 및 DB 생성 중..."):
            data_utils.process_and_embed(str(DATA_DIRECTORY), status)
        st.rerun()

# --- 메인 화면 탭 ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Q&A", "📚 지식 베이스 탐색기", "🗂️ Rule & 용어 정리"])

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

with tab3:
    st.header("Rule & 개념 용어 자동 분류")
    if not os.path.exists(JSON_FILE_PATH):
        st.info(
            "knowledge_base.json 파일이 없습니다. 사이드바에서 데이터 업로드 후 '데이터베이스 재생성'을 실행해주세요."
        )
    else:
        rc_df = data_utils.load_rule_concept_dataframe()
        if rc_df.empty:
            st.info("분류할 데이터가 없습니다. 먼저 지식 베이스를 생성해주세요.")
        else:
            st.caption(
                f"총 {len(rc_df)}개의 항목을 자동으로 'rule'과 'concept'으로 분류했습니다. 필요한 경우 직접 수정 후 저장할 수 있습니다."
            )

            distribution = rc_df["rc_category"].value_counts().to_dict()
            col_stats = st.columns(len(distribution) or 1)
            for (label, count), column in zip(distribution.items(), col_stats):
                with column:
                    st.metric(label=f"{label.upper()}", value=count)

            editable_df = rc_df.copy()
            editable_df["chunk_id"] = editable_df["chunk_id"].astype(str)
            editable_df["text_preview"] = editable_df["text"].apply(
                lambda text: (text[:180] + "...") if len(text) > 180 else text
            )

            display_columns = [
                "chunk_id",
                "source_file",
                "title",
                "rc_category",
                "key_phrases",
                "summary",
                "notes",
                "text_preview",
            ]

            editor = st.data_editor(
                editable_df[display_columns],
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "chunk_id": st.column_config.TextColumn("Chunk ID", disabled=True, width="small"),
                    "source_file": st.column_config.TextColumn("원본 파일", disabled=True, width="small"),
                    "title": st.column_config.TextColumn("제목", disabled=True, width="medium"),
                    "rc_category": st.column_config.SelectboxColumn(
                        "분류", options=sorted(data_utils.RULE_CONCEPT_ALLOWED), help="rule/concept 중 하나를 선택하세요."
                    ),
                    "key_phrases": st.column_config.TextColumn(
                        "핵심 키워드", help="쉼표로 구분된 키워드를 입력하세요.", width="medium"
                    ),
                    "summary": st.column_config.TextColumn(
                        "요약", help="핵심 내용을 간단히 정리하세요.", width="large"
                    ),
                    "notes": st.column_config.TextColumn("비고", width="medium"),
                    "text_preview": st.column_config.TextColumn(
                        "내용 미리보기", disabled=True, width="large", help="원문 일부를 참고하세요."
                    ),
                },
                key="rule_concept_editor",
            )

            updated_df = rc_df.set_index("chunk_id")
            editor_no_preview = editor.drop(columns=["text_preview"]).set_index("chunk_id")
            for column in ["rc_category", "key_phrases", "summary", "notes"]:
                if column in editor_no_preview.columns:
                    updated_df[column] = editor_no_preview[column]
            updated_df = updated_df.reset_index()

            st.divider()
            save_col, download_col, upload_col = st.columns([1, 1, 1])

            with save_col:
                if st.button("변경 사항 저장", type="primary"):
                    try:
                        data_utils.persist_rule_concept_dataframe(updated_df)
                        st.success("CSV와 knowledge_base.json이 업데이트되었습니다.")
                        st.experimental_rerun()
                    except Exception as exc:
                        st.error(f"저장 중 오류가 발생했습니다: {exc}")

            with download_col:
                try:
                    validated = data_utils.validate_rule_concept_dataframe(updated_df)
                    csv_buffer = io.StringIO()
                    validated.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="CSV 다운로드",
                        data=csv_buffer.getvalue(),
                        file_name="rule_concept_dataset.csv",
                        mime="text/csv",
                    )
                except Exception as exc:
                    st.error(f"CSV 생성 중 오류: {exc}")

            with upload_col:
                uploaded_csv = st.file_uploader(
                    "CSV 업로드", type="csv", key="rule_concept_csv_uploader"
                )
                if uploaded_csv is not None:
                    try:
                        uploaded_df = pd.read_csv(uploaded_csv)
                        data_utils.persist_rule_concept_dataframe(uploaded_df)
                        st.success("업로드한 CSV 내용을 적용했습니다.")
                        st.experimental_rerun()
                    except Exception as exc:
                        st.error(f"CSV 업로드 중 오류: {exc}")

