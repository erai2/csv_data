import re
import json
import os
import glob
from collections import Counter
from typing import List, Dict, Any

import pandas as pd
import streamlit as st

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- 설정 ---
DB_DIRECTORY = os.path.join(MODULE_DIR, "chroma_db")
JSON_FILE_PATH = os.path.join(MODULE_DIR, "knowledge_base.json")
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RULE_CONCEPT_CSV_PATH = os.path.join(MODULE_DIR, "rule_concept_dataset.csv")

RULE_KEYWORDS = [
    "규칙",
    "rule",
    "원칙",
    "법칙",
    "프로세스",
    "절차",
    "방법",
    "체계",
    "조건",
    "판단",
    "제압",
    "분석",
    "상법",
    "기준",
]

CONCEPT_KEYWORDS = [
    "용어",
    "개념",
    "정의",
    "의미",
    "설명",
    "특징",
    "관계",
    "종류",
    "요소",
    "핵심",
]

STOPWORDS = {
    "그리고",
    "그러나",
    "하지만",
    "또한",
    "이는",
    "등",
    "the",
    "and",
    "that",
    "with",
    "from",
    "이다",
    "있는",
    "하여",
    "위해",
}

RULE_CONCEPT_ALLOWED = {"rule", "concept", "other"}
RULE_CONCEPT_COLUMNS = [
    "chunk_id",
    "source_file",
    "title",
    "rc_category",
    "key_phrases",
    "summary",
    "text",
    "notes",
]

def parse_myeongri_document(text: str, source_file: str) -> List[Dict[str, Any]]:
    """명리학 문서를 분석하여 체계적인 지식 chunk로 변환합니다."""
    structured_data = []
    delimiter_pattern = r'\n(?=Part\d+.*?|#\d+.*?|<사례\s\d+>)'
    blocks = re.split(delimiter_pattern, text.strip())

    for block in blocks:
        block = block.strip()
        if not block: continue
        
        chunk = {"source_file": source_file}
        lines = block.split('\n')
        first_line = lines[0].strip()

        case_match = re.match(r'^<사례\s(\d+)>', first_line)
        section_match = re.match(r'^(Part\d+.*?|#\d+.*?)', first_line)

        if case_match:
            chunk["category"] = "사례"
            chunk["sub_category"] = f"사례 {case_match.group(1)}"
            case_content = block
            
            title_match = re.search(r'^/제목/(.*)', case_content, re.MULTILINE)
            if title_match:
                chunk["title"] = title_match.group(1).strip()
                case_content = case_content.replace(title_match.group(0), '', 1)
            else:
                chunk["title"] = re.sub(r'<사례\s\d+>\s*', '', first_line).strip() or chunk["sub_category"]
            
            structure_match = re.search(r'^구성/(.*)', case_content, re.MULTILINE)
            if structure_match:
                chunk["structure"] = structure_match.group(1).strip()
                case_content = case_content.replace(structure_match.group(0), '', 1)
            else:
                chunk["structure"] = ""

            cleaned_text = re.sub(r'^<사례\s\d+>.*?\n', '', case_content, count=1).strip()
            chunk["text"] = cleaned_text

        elif section_match:
            chunk["category"] = "용어/규칙"
            chunk["sub_category"] = section_match.group(1).strip()
            chunk["title"] = chunk["sub_category"]
            chunk["text"] = block
        else:
            chunk["category"] = "기타"
            chunk["sub_category"] = "서론"
            chunk["title"] = lines[0] if len(lines[0]) < 50 else "소개"
            chunk["text"] = block
            
        structured_data.append(chunk)
    return structured_data

def process_and_embed(input_dir: str, status_placeholder):
    """지정된 디렉토리의 모든 .md, .txt 파일을 처리하여 벡터 DB를 생성합니다."""
    all_chunks = []
    files_to_process = glob.glob(os.path.join(input_dir, "*.md")) + glob.glob(os.path.join(input_dir, "*.txt"))

    if not files_to_process:
        status_placeholder.error(f"오류: '{input_dir}' 디렉토리에서 처리할 파일(.md, .txt)이 없습니다. 사이드바에서 파일을 업로드해주세요.")
        return

    status_placeholder.info(f"📁 총 {len(files_to_process)}개의 파일을 처리합니다...")
    for filepath in files_to_process:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='cp949') as f: content = f.read()
        except Exception as e:
            status_placeholder.error(f"오류: '{filename}' 파일 읽기 중 오류 발생: {e}")
            continue
            
        chunks = parse_myeongri_document(content, filename)
        all_chunks.extend(chunks)

    unique_chunks = []
    seen_signatures = set()
    for chunk in all_chunks:
        signature = (chunk.get('title', ''), chunk.get('text', ''))
        if signature not in seen_signatures:
            unique_chunks.append(chunk)
            seen_signatures.add(signature)
    
    status_placeholder.info(f"✨ 중복 제거 완료: {len(all_chunks)}개 chunk -> {len(unique_chunks)}개 고유 chunk")
    
    for i, chunk in enumerate(unique_chunks):
        chunk['chunk_id'] = f"{i+1:03d}"

    # Save the parsed data to knowledge_base.json
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(unique_chunks, f, ensure_ascii=False, indent=2)
    
    documents = []
    for chunk in unique_chunks:
        page_content = f"제목: {chunk.get('title', '')}\n카테고리: {chunk.get('sub_category', '')}\n내용: {chunk.get('text', '')}"
        metadata = {k: v for k, v in chunk.items() if k != 'text'}
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)
    
    if not documents:
        status_placeholder.warning("처리할 문서가 없어 벡터 DB 구축을 건너뜁니다.")
        return

    status_placeholder.info(f"🧠 임베딩 모델 '{EMBEDDING_MODEL_NAME}'을(를) 로드합니다...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    status_placeholder.info(f"💾 '{DB_DIRECTORY}' 디렉토리에 벡터 데이터베이스를 구축합니다...")
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_DIRECTORY
    )

    status_placeholder.success("✅ 벡터 데이터베이스 구축 및 저장이 완료되었습니다!")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _generate_summary(text: str, max_length: int = 160) -> str:
    cleaned = _clean_text(text)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3] + "..."


def _extract_keywords(text: str, top_n: int = 5) -> str:
    tokens = re.findall(r"[A-Za-z가-힣]{2,}", text or "")
    filtered = [token for token in tokens if token not in STOPWORDS]
    if not filtered:
        return ""
    counts = Counter(token for token in filtered)
    ranked = [word for word, _ in counts.most_common(top_n)]
    return ", ".join(ranked)


def _auto_classify_rule_concept(chunk: Dict[str, Any]) -> str:
    explicit = _clean_text(chunk.get("rc_category"))
    if explicit:
        lower = explicit.lower()
        if lower in RULE_CONCEPT_ALLOWED:
            return lower

    category_hint = _clean_text(chunk.get("category")).lower()
    sub_category_hint = _clean_text(chunk.get("sub_category")).lower()
    title_hint = _clean_text(chunk.get("title")).lower()
    text_hint = _clean_text(chunk.get("text"))[:200].lower()

    combined = " ".join(filter(None, [category_hint, sub_category_hint, title_hint, text_hint]))

    if "사례" in category_hint or "case" in category_hint:
        return "other"

    if any(keyword in category_hint for keyword in ["규칙", "rule"]):
        return "rule"
    if any(keyword in sub_category_hint for keyword in ["규칙", "rule", "법"]):
        return "rule"

    if any(keyword in category_hint for keyword in ["용어", "term"]):
        return "concept"
    if any(keyword in sub_category_hint for keyword in ["용어", "개념", "정의"]):
        return "concept"

    if any(keyword.lower() in combined for keyword in RULE_KEYWORDS):
        return "rule"
    if any(keyword.lower() in combined for keyword in CONCEPT_KEYWORDS):
        return "concept"

    return "concept"


def load_rule_concept_dataframe(
    json_path: str = JSON_FILE_PATH, csv_path: str = RULE_CONCEPT_CSV_PATH
) -> pd.DataFrame:
    if not os.path.exists(json_path):
        return pd.DataFrame(columns=RULE_CONCEPT_COLUMNS)

    with open(json_path, "r", encoding="utf-8") as f:
        knowledge_chunks = json.load(f)

    rows: List[Dict[str, Any]] = []
    for index, chunk in enumerate(knowledge_chunks, start=1):
        chunk_id = str(chunk.get("chunk_id") or chunk.get("id") or f"{index:03d}")
        text = chunk.get("text", "")
        rows.append(
            {
                "chunk_id": chunk_id,
                "source_file": chunk.get("source_file", ""),
                "title": chunk.get("title", ""),
                "rc_category": _auto_classify_rule_concept(chunk),
                "key_phrases": chunk.get("rc_keywords") or _extract_keywords(text),
                "summary": chunk.get("rc_summary") or _generate_summary(text),
                "text": text,
                "notes": chunk.get("rc_notes", ""),
            }
        )

    df = pd.DataFrame(rows, columns=RULE_CONCEPT_COLUMNS)

    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path, dtype={"chunk_id": str})
        if not existing_df.empty:
            existing_df = existing_df.set_index("chunk_id")
            df = df.set_index("chunk_id")
            for column in existing_df.columns:
                if column in df.columns:
                    df[column] = existing_df[column].combine_first(df[column])
                else:
                    df[column] = existing_df[column]
            df = df.reset_index()
        else:
            df = df.reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    df = df.fillna({"rc_category": "concept", "summary": "", "key_phrases": "", "notes": ""})
    df["rc_category"] = df["rc_category"].apply(lambda val: str(val).lower() if pd.notna(val) else "concept")
    df.loc[~df["rc_category"].isin(RULE_CONCEPT_ALLOWED), "rc_category"] = "concept"
    df = df.sort_values(["source_file", "chunk_id"]).reset_index(drop=True)
    return df


def validate_rule_concept_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [col for col in RULE_CONCEPT_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"CSV에 필요한 컬럼이 없습니다: {', '.join(missing_columns)}")

    validated = df.copy()
    validated["chunk_id"] = validated["chunk_id"].astype(str)
    validated["rc_category"] = (
        validated["rc_category"].fillna("concept").astype(str).str.lower()
    )
    validated.loc[~validated["rc_category"].isin(RULE_CONCEPT_ALLOWED), "rc_category"] = "concept"
    for column in ["key_phrases", "summary", "notes"]:
        validated[column] = validated[column].fillna("").apply(_clean_text)
    validated["text"] = validated["text"].fillna("")
    return validated


def update_knowledge_base_with_rc(
    df: pd.DataFrame, json_path: str = JSON_FILE_PATH
) -> None:
    if not os.path.exists(json_path):
        return

    with open(json_path, "r", encoding="utf-8") as f:
        knowledge_chunks = json.load(f)

    chunk_map = {
        str(chunk.get("chunk_id") or chunk.get("id")): chunk for chunk in knowledge_chunks
    }

    for _, row in df.iterrows():
        key = str(row.get("chunk_id"))
        target = chunk_map.get(key)
        if not target:
            continue
        target["rc_category"] = row.get("rc_category", "")
        target["rc_summary"] = row.get("summary", "")
        target["rc_keywords"] = row.get("key_phrases", "")
        target["rc_notes"] = row.get("notes", "")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_chunks, f, ensure_ascii=False, indent=2)


def persist_rule_concept_dataframe(
    df: pd.DataFrame,
    csv_path: str = RULE_CONCEPT_CSV_PATH,
    json_path: str = JSON_FILE_PATH,
) -> None:
    validated = validate_rule_concept_dataframe(df)
    validated.to_csv(csv_path, index=False, encoding="utf-8-sig")
    update_knowledge_base_with_rc(validated, json_path=json_path)

