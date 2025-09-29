import re
import pandas as pd
from system import SajuAnalyzer
from db import fetch_table

DB_PATH = "suri.db"

def search_db(query: str):
    """DB에서 개념과 규칙을 검색합니다."""
    # 1. 개념(Concepts) 테이블에서 정확히 일치하는 용어 검색
    concepts_df = fetch_table(DB_PATH, "concepts")
    exact_match = concepts_df[concepts_df['name'] == query]
    if not exact_match.empty:
        return f"**✅ 개념: {query}**\n\n{exact_match.iloc[0]['definition']}"

    # 2. 규칙(Rules) 테이블에서 키워드가 포함된 규칙 검색
    rules_df = fetch_table(DB_PATH, "rules")
    # condition_text 또는 result_text에 query가 포함된 모든 행을 찾습니다.
    # `na=False`는 NaN 값을 False로 처리하여 오류를 방지합니다.
    related_rules = rules_df[
        rules_df['condition_text'].str.contains(query, na=False) |
        rules_df['result_text'].str.contains(query, na=False)
    ]
    
    if not related_rules.empty:
        response = f"**🔍 '{query}'와(과) 관련된 규칙**\n\n"
        for _, row in related_rules.iterrows():
            response += f"- {row['condition_text']} → {row['result_text']}\n"
        return response
    
    return None

def analyze_saju_and_get_rules(saju_text: str):
    """사주를 분석하고 관련된 규칙을 DB에서 찾아 반환합니다."""
    try:
        analyzer = SajuAnalyzer(saju_text)
        analysis = analyzer.analyze() # system.py의 분석 기능 실행
        
        response = f"**📜 사주 분석 결과: {saju_text}**\n\n"
        
        # 분석된 각 항목(합, 충 등)에 대해 관련된 규칙을 DB에서 검색
        all_relations = (
            analysis.get("합충형파천", []) +
            analysis.get("삼합", []) +
            analysis.get("육합", []) +
            analysis.get("암합", [])
        )

        found_rules_count = 0
        # 분석 결과(예: '寅충申')에서 한 글자씩(예: '충', '형') 키워드를 추출
        for relation in all_relations:
            # 정규표현식을 사용해 한글 키워드(충, 형, 합 등)만 추출
            keywords = re.findall(r'[가-힣]+', relation)
            for keyword in keywords:
                if len(keyword) > 1: continue # '삼합' 같은 단어는 제외
                
                # 키워드로 규칙 검색
                rules_df = fetch_table(DB_PATH, "rules")
                matched_rules = rules_df[
                    rules_df['condition_text'].str.contains(keyword, na=False) |
                    rules_df['result_text'].str.contains(keyword, na=False)
                ]
                
                if not matched_rules.empty:
                    response += f"**🔎 '{relation}' 관련 규칙:**\n"
                    for _, row in matched_rules.head(3).iterrows(): # 너무 길지 않게 3개만 표시
                        response += f"- {row['condition_text']} → {row['result_text']}\n"
                    response += "\n"
                    found_rules_count += len(matched_rules)

        if found_rules_count == 0:
            response += "DB에서 분석 결과와 관련된 규칙을 찾지 못했습니다."
            
        return response

    except Exception as e:
        return f"사주 분석 중 오류가 발생했습니다: {e}"


def get_chatbot_response(query: str):
    """사용자 입력에 따라 적절한 답변을 생성합니다."""
    query = query.strip()
    
    # 1. 입력이 사주 명식 형식인지 확인 (예: 庚子 辛巳 癸卯 甲寅)
    saju_pattern = re.compile(r'^[가-힣]{2}\s+[가-힣]{2}\s+[가-힣]{2}\s+[가-힣]{2}$')
    if saju_pattern.match(query):
        return analyze_saju_and_get_rules(query)

    # 2. 사주 명식이 아니라면 DB 검색
    db_response = search_db(query)
    if db_response:
        return db_response

    # 3. 아무 결과도 찾지 못한 경우
    return f"'{query}'에 대한 정보를 찾을 수 없습니다. 명확한 키워드(예: '공망')나 정확한 사주 명식(예: '庚子 辛巳 癸卯 甲寅')을 입력해 주세요."