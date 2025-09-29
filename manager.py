import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_concepts(db_path="suri.db", threshold=0.7):
    # (이 함수는 기존과 동일합니다 - 데이터 관리 탭에서 사용)
    from db import fetch_table
    
    df = fetch_table(db_path, "concepts")
    if df.empty or len(df) < 2:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['definition'])
    cosine_sim_matrix = cosine_similarity(tfidf_matrix)
    
    groups = []
    processed_indices = set()

    for i in range(len(df)):
        if i in processed_indices:
            continue

        similar_indices = [j for j, sim in enumerate(cosine_sim_matrix[i]) if sim > threshold and i != j]

        if similar_indices:
            current_group_indices = {i} | set(similar_indices)
            group_df = df.iloc[list(current_group_indices)].copy()
            avg_similarity = cosine_sim_matrix[i][similar_indices].mean()
            
            groups.append({
                "avg_similarity": avg_similarity,
                "items": group_df.to_dict('records')
            })
            processed_indices.update(current_group_indices)
            
    groups.sort(key=lambda x: x['avg_similarity'], reverse=True)
    return groups

# --- 아래 함수가 새로 추가되었습니다 ---
def check_similarity_before_save(new_concepts: list, db_path="suri.db", threshold=0.8):
    """
    새로 추가될 개념(new_concepts)과 DB의 기존 개념 간의 유사도를 검사합니다.
    
    :param new_concepts: 파싱된 새로운 개념 데이터 리스트
    :param db_path: DB 경로
    :param threshold: 중복으로 판단할 유사도 임계값
    :return: 유사 항목 목록. 없으면 빈 리스트.
    """
    from db import fetch_table
    
    existing_df = fetch_table(db_path, "concepts")
    
    # DB가 비어있거나 새 개념이 없으면 검사할 필요 없음
    if existing_df.empty or not new_concepts:
        return []

    new_df = pd.DataFrame(new_concepts)
    
    # 기존 정의와 새로운 정의를 합쳐서 TF-IDF 벡터화 준비
    all_definitions = pd.concat([existing_df['definition'], new_df['definition']], ignore_index=True)
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_definitions)
    
    # 기존 데이터와 새로운 데이터 간의 코사인 유사도 계산
    # (기존 데이터 수, 전체 데이터 수)
    num_existing = len(existing_df)
    cosine_sim_matrix = cosine_similarity(tfidf_matrix[num_existing:], tfidf_matrix[:num_existing])
    
    found_duplicates = []
    
    # 각 새로운 개념에 대해 유사도 검사
    for i in range(len(new_df)):
        # i번째 새로운 개념과 가장 유사한 기존 개념의 인덱스와 점수 찾기
        most_similar_idx = cosine_sim_matrix[i].argmax()
        max_similarity_score = cosine_sim_matrix[i][most_similar_idx]
        
        if max_similarity_score > threshold:
            found_duplicates.append({
                "new_item_name": new_df.iloc[i]['name'],
                "existing_item_name": existing_df.iloc[most_similar_idx]['name'],
                "similarity": max_similarity_score
            })
            
    return found_duplicates