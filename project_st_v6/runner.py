from saju_system import SajuAnalyzer
from parser import parse_documents

if __name__ == "__main__":
    print("📂 문서 파싱...")
    parsed = parse_documents("docs")

    analyzer = SajuAnalyzer(parsed_data_path="parsed/parsed_keywords.json")
    report = analyzer.build_report()

    print(report)

    with open("reports/analysis.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("📑 저장 완료: reports/analysis.md")
