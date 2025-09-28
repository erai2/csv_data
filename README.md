# csv_data

## 실행 전 준비
- Python 3.10 이상이 설치되어 있어야 합니다.
- (선택) 가상환경을 사용하는 것을 권장합니다.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

필수 패키지는 프로젝트 루트의 `project_st_v6/requirements.txt` 에 정의되어 있습니다.

```bash
pip install -r project_st_v6/requirements.txt
```

## 실행 방법

### 1. Streamlit 웹 앱 실행
문서를 업로드하고 분석 리포트를 생성하는 웹 UI를 사용하려면 다음 명령을 실행합니다.

```bash
cd project_st_v6
streamlit run app.py
```

브라우저에서 표시되는 주소(기본값: http://localhost:8501)를 열어 인터페이스에 접근할 수 있습니다.

### 2. 커맨드라인 리포트 생성기 실행
로컬에 저장된 문서를 기반으로 리포트를 생성하려면 아래 명령을 실행합니다.

```bash
cd project_st_v6
python runner.py
```

`docs/` 폴더의 문서를 파싱한 뒤, 결과 리포트를 `reports/analysis.md` 로 저장합니다.

## 추가 참고
- `parsed_all.json` 파일이 존재하면 Streamlit 애플리케이션의 분석에 사용됩니다.
- `runner.py` 는 `docs/` 폴더 내 파일을 기반으로 자동으로 리포트를 생성합니다.
