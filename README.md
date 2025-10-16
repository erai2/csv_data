# 수암명리 데이터 시스템

이 저장소는 Streamlit 기반의 명리 데이터 관리/탐색 도구를 제공합니다. 기본 `app.py`는 SQLite 데이터베이스(`suri_db_system/db/suri_manual.db`)를 사용하고, `app_upgraded.py`는 전문가용 JSON 지식 베이스를 활용합니다.

## 구성 요소

| 경로 | 설명 |
| --- | --- |
| `app.py` | 규칙/용어/사례를 SQLite DB로 관리하는 기본 Streamlit 앱 |
| `app_upgraded.py` | 통합 지식 베이스(`suam_master_data.json`)를 시각화하는 전문가용 Streamlit 앱 |
| `suri_db_system/` | 스키마, 샘플 JSON, DB 초기화 스크립트가 포함된 폴더 |
| `data/templates/suam_master_data.template.json` | 전문가용 앱을 위한 JSON 템플릿 (실제 데이터는 `.gitignore`) |
| `utils/` | DB 초기화 및 추출 로직 등 공용 유틸리티 |

## 환경 구성

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

필요 라이브러리에는 `streamlit`, `pandas`, `pdfplumber`, `python-docx`, `pyvis`가 포함됩니다.

## 전문가용 지식 베이스 앱 사용법 (`app_upgraded.py`)

1. `data/templates/suam_master_data.template.json` 파일을 복사하여 `suam_master_data.json` 이름으로 저장합니다. (실제 데이터 파일은 `.gitignore`에 등록되어 GitHub에 업로드되지 않습니다.)
2. 필요에 맞게 JSON 내용을 수정합니다.
3. 아래 명령어로 앱을 실행합니다.
   ```bash
   streamlit run app_upgraded.py
   ```
4. 왼쪽 사이드바에서 홈, 용어 사전, 구조론, 주제별 분석, 심화 개념, 사례 연구 메뉴를 탐색할 수 있습니다.

앱 실행 시 `suam_master_data.json`이 없으면 템플릿 경로를 안내하며 중단되므로, 데이터 파일을 먼저 준비해 주세요.

## 기존 SQLite 앱 사용법 (`app.py`)

1. `suri_db_system/scripts/db_insert.py`를 실행하여 스키마와 샘플 데이터를 초기화합니다.
   ```bash
   python suri_db_system/scripts/db_insert.py
   ```
2. Streamlit 앱을 실행합니다.
   ```bash
   streamlit run app.py
   ```
3. 문서를 업로드해 자동 추출을 수행하거나, 등록된 규칙/용어/사례를 탐색하고 시각화 탭을 확인할 수 있습니다.

## 보안/데이터 정책

- 실제 운영 데이터(`suam_master_data.json`, `suri_db_system/data/` 등)는 `.gitignore`에 포함되어 저장소에 커밋되지 않습니다.
- 추가적인 비공개 설정은 `.env`, `.streamlit/` 디렉터리를 활용해 관리할 수 있습니다.

## 테스트

앱 실행 전 `python -m streamlit` 관련 명령이 정상 동작하는지 확인하고, 데이터 파일 경로를 재검토하세요.
