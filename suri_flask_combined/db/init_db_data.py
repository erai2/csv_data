from db_utils import initialize_db, insert_data

# DB 초기화
initialize_db()

# 기본 데이터 입력
insert_data("forces", {
    "name": "목화세",
    "elements": "木,火",
    "traits": "표현, 창조, 추진",
    "interpretation": "목화세가 금수세를 제압하면 재/관 취득"
})

insert_data("forces", {
    "name": "금수세",
    "elements": "金,水",
    "traits": "통제, 자원, 생존",
    "interpretation": "금수세가 목화세를 제압하면 재/관 상실"
})

insert_data("geokuk", {
    "name": "官印相生格",
    "condition": "官이 印을 生하거나 印이 官을 生하는 구조",
    "explanation": "관직·명예 중심 격국",
    "job_field": "공무원, 권력기관, 법조계"
})

insert_data("patterns", {
    "trigger": "食神生財格",
    "outcome": "사업, 생산, 기술직",
    "category": "직업"
})
