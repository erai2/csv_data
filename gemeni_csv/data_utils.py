import re
import json
import os
import glob
from typing import List, Dict, Any
import streamlit as st

from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- 설정 ---
DB_DIRECTORY = "chroma_db"
JSON_FILE_PATH = "knowledge_base.json"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

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

