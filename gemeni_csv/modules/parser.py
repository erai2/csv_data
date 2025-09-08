import re
import json
from typing import List, Dict, Any

# ===================================================================
# Part 1: 사례(Case) 분석 파서 (기존 코드)
# ===================================================================

def parse_myeongri_text(text: str) -> List[Dict[str, Any]]:
    """
    수암명리 원문 텍스트에서 '사례'들을 파싱하여 구조화된 JSON 객체 리스트로 변환합니다.
    """
    case_blocks = re.split(r'\n(?=사례 \d+:)', text.strip())
    structured_data = []

    for block in case_blocks:
        if not block.strip():
            continue

        data: Dict[str, Any] = {}
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        data['title'] = lines[0] if lines else ""
        data['일주'] = lines[1] if len(lines) > 1 else ""
        data['지지'] = lines[2] if len(lines) > 2 else ""

        current_section = None
        data['구조분석'] = []
        data['해석'] = []
        data['핵심십신관계'] = {}
        interpretation_lines = []

        for line in lines[3:]:
            if line.startswith('■ 구조 분석:'):
                current_section = '구조분석'
                continue
            elif line.startswith('■ 해석 요약:'):
                current_section = '해석'
                continue
            elif line.startswith('■ 구조 유형:'):
                try:
                    data['분류'] = lines[lines.index(line) + 1]
                except IndexError:
                    data['분류'] = ""
                current_section = '분류'
                continue
            elif line.startswith('■ 관련 제압방식:'):
                try:
                    content = lines[lines.index(line) + 1]
                    data['제압방식'] = [item.strip() for item in content.split(',')]
                except IndexError:
                    data['제압방식'] = []
                current_section = '제압방식'
                continue

            if current_section == '구조분석':
                data['구조분석'].append(line)
            elif current_section == '해석':
                interpretation_lines.append(line)

        for line in interpretation_lines:
            match = re.search(r'(\w+日主)에게\s*([^,]+?)는\s*([^,]+)', line)
            if match:
                subject, obj, relation = match.groups()
                if subject not in data['핵심십신관계']:
                    data['핵심십신관계'][subject] = {}
                data['핵심십신관계'][subject][obj.strip()] = relation.strip()
                remaining_parts = line.split(match.group(0))[-1]
                extra_matches = re.findall(r',\s*([^,]+?)는\s*([^,]+)', remaining_parts)
                for extra_obj, extra_relation in extra_matches:
                    data['핵심십신관계'][subject][extra_obj.strip()] = extra_relation.strip()
            else:
                data['해석'].append(line)

        structured_data.append(data)

    return structured_data

# ===================================================================
# Part 2: 문서(Document) 구조화 파서 (신규 추가)
# ===================================================================

def classify_chunk(title: str, text: str) -> Dict[str, str]:
    """
    제목과 본문 내용을 기반으로 chunk의 category와 sub_category를 추론합니다.
    """
    # 키워드 기반 분류 규칙
    term_keywords = ['개념', '정의', '록', '원신', '십신', '육친']
    rule_keywords = ['해석체계', '제압방식', '분석방법', '이법', '상법', '구조']

    content_for_classification = (title + " " + text[:100]).lower()

    if any(keyword in content_for_classification for keyword in term_keywords):
        category = "용어"
    elif any(keyword in content_for_classification for keyword in rule_keywords):
        category = "규칙"
    else:
        category = "기타" # 기본값

    # sub_category는 title에서 핵심 단어를 추출 (간단한 버전)
    sub_category = re.sub(r'의|및|개념|정의|사례', '', title).strip()
    
    return {"category": category, "sub_category": sub_category}


def parse_document_chunks(text: str, source_file: str) -> List[Dict[str, Any]]:
    """
    일반 문서를 의미있는 지식 조각(chunk)으로 분할하고 JSON으로 구조화합니다.
    """
    # "---"와 같은 명시적 구분자로 문서를 분할합니다.
    chunks = re.split(r'\n---\n', text.strip())
    structured_data = []

    for i, chunk_text in enumerate(chunks):
        if not chunk_text.strip():
            continue

        lines = [line.strip() for line in chunk_text.split('\n') if line.strip()]
        
        title = lines[0] if lines else "제목 없음"
        full_text = "\n".join(lines[1:])

        # 내용 기반으로 카테고리 분류
        classification = classify_chunk(title, full_text)

        chunk_data = {
            "chunk_id": f"{i+1:03d}",
            "category": classification["category"],
            "sub_category": classification["sub_category"],
            "title": title,
            "text": full_text,
            "source_file": source_file
        }
        structured_data.append(chunk_data)
        
    return structured_data


def convert_file(input_filepath: str, output_filepath: str, mode: str):
    """
    파일을 읽어 선택된 모드(cases or docs)에 따라 변환을 수행합니다.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if mode == 'cases':
            parsed_data = parse_myeongri_text(content)
        elif mode == 'docs':
            parsed_data = parse_document_chunks(content, input_filepath)
        else:
            raise ValueError("mode는 'cases' 또는 'docs'여야 합니다.")

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ '{mode}' 모드 변환 완료: '{input_filepath}' -> '{output_filepath}'")
        print(f"총 {len(parsed_data)}개의 항목이 처리되었습니다.")

    except FileNotFoundError:
        print(f"❌ 오류: 입력 파일 '{input_filepath}'을(를) 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# --- 실행 ---
if __name__ == '__main__':
    # "cases" 또는 "docs" 모드를 선택하여 실행하세요.
    # 'cases': 사례(사주, 구조분석 등)를 추출합니다.
    # 'docs': 일반 문서(용어, 규칙 등)를 지식 chunk로 구조화합니다.
    MODE_TO_RUN = "docs"

    if MODE_TO_RUN == "cases":
        # 사례 분석 실행 예시
        INPUT_FILE = "Book5_new.md" 
        OUTPUT_FILE = "cases_database.json"
        # 테스트를 위해 임시 입력 파일을 생성할 수 있습니다.
        # with open(INPUT_FILE, "w", encoding="utf-8") as f:
        #     f.write("사례 10: ... (내용 생략)")
        convert_file(INPUT_FILE, OUTPUT_FILE, mode='cases')

    elif MODE_TO_RUN == "docs":
        # 문서 구조화 실행 예시
        INPUT_FILE = "sauman-ri-rules.txt"
        OUTPUT_FILE = "knowledge_chunks.json"
        
        # 테스트를 위한 임시 입력 파일 생성
        # (실제 파일이 있다면 이 부분은 주석 처리)
        example_doc_text = """
록(祿)과 원신(原身)의 개념 및 사주 적용 사례
록(祿)과 원신(原身)은 사주팔자에서 천간과 지지의 관계, 특히 특정 기운이 어떻게 현실에서 발현되고 작용하는지를 이해하는 중요한 개념입니다.
록(祿)과 원신(原身)의 정의
•\t록(祿): 천간의 기운이 지지에 뿌리를 내려 권력을 행사하거나 주도적인 역할을 하는 상태를 의미합니다.
•\t원신(原身): 지지에 있던 기운이 천간으로 뻗어 나와(延伸) 작용하는 것을 말합니다.
---
수암명리 해석체계 및 정의
flowchart TD
A[\"수암명리 해석체계\"] --> B[\"주요 개념\"]
B --> C[\"주위(영지)와 빈위(타지)\"]
B --> D[\"간지호통(干支互通)\"]
수암명리는 전통적인 명리학과 달리 일간이 추구하는 재(財)와 관(官)을 어떤 방식으로 제압하는지에 초점을 맞추고 있습니다.
---
수암명리 분석방법 및 제압방식
Part4. 수암명리의 분석방법
수암명리의 분석방법에는 이법(理法), 상법(象法), 실전 분석기법 세 가지가 있습니다.
위에서 연구한 5가지의 제압방식이 있지만 실제로 각 사주를 분석할 때는 한가지의 제압방식이 아닌 두개이상의 제압 방식이 존재한다.
"""
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write(example_doc_text)

        convert_file(INPUT_FILE, OUTPUT_FILE, mode='docs')

