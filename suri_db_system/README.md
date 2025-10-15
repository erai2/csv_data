# Suri DB System

수암명리 시스템에서 활용할 수 있는 SQLite 기반 관계형 데이터베이스 구조와 자동 데이터 삽입 스크립트입니다. 예시 데이터와 스키마, 실행 스크립트를 포함하고 있어 즉시 DB를 초기화하고 데이터를 적재할 수 있습니다.

## 디렉터리 구조

```
suri_db_system/
├── db/
│   └── suri_manual.db           # 생성될 SQLite DB 파일 (gitignore 대상)
├── schema/
│   └── suri_db_schema.sql       # 테이블 및 인덱스 정의
├── scripts/
│   └── db_insert.py             # DB 초기화 및 데이터 삽입 스크립트
└── data/
    ├── rules.json               # 규칙 데이터
    ├── terms.json               # 용어 데이터
    └── cases.json               # 사례 데이터
```

## 사용 방법

1. 가상환경을 활성화하고 `requirements.txt`에 정의된 패키지를 설치합니다.
2. 프로젝트 루트(`/workspace/csv_data`)에서 다음 명령을 실행합니다.

```bash
python suri_db_system/scripts/db_insert.py
```

3. `suri_db_system/db/suri_manual.db` 파일이 생성되고 예시 데이터가 적재됩니다. 해당 파일은 `.gitignore`에 의해 버전 관리에서 제외됩니다.

## Streamlit 앱 연동

- 루트의 `app.py`는 동일한 `suri_db_system/db/suri_manual.db` 파일을 직접 사용합니다.
- 앱을 처음 실행하면 DB가 자동으로 초기화되며, 테이블이 비어 있는 경우 이 디렉터리의 예시 JSON 데이터로 채워집니다.
- Streamlit UI에서는 사례 상세 화면에서 연결된 규칙/용어까지 함께 확인할 수 있습니다.

## 데이터 연계 방식

- `rules`, `terms`, `cases` 테이블은 각각 규칙, 용어, 사례 정보를 보관합니다.
- `case_rule_link`, `case_term_link`는 사례와 규칙/용어를 연결하는 다대다 관계 테이블입니다.
- JSON 데이터의 `linked_rules`, `linked_terms` 값은 규칙/용어의 **식별자(ID)** 와 매핑되어 관계가 생성됩니다.

## 주의 사항

- 스크립트 실행 전 `data/` 디렉터리의 JSON 파일 구조를 유지해주세요.
- 예시 데이터는 참고용이며, 실제 데이터로 교체하여 사용할 수 있습니다.
- 민감하거나 대용량의 실제 DB 파일은 배포/배션 관리 시 `.gitignore` 규칙을 통해 안전하게 관리하세요.
