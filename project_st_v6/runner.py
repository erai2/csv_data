from pathlib import Path

from parser import parse_documents
from system import SajuAnalyzer

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    docs_dir = base_dir / "docs"
    parsed_output = base_dir / "parsed_all.json"
    report_path = base_dir / "reports" / "analysis.md"

    print("📂 문서 파싱...")
    parsed = parse_documents(docs_dir, save_path=parsed_output)
    print(f"  └ 처리된 문서 수: {len(parsed)}")

    analyzer = SajuAnalyzer(parsed_data_path=str(parsed_output))
    report = analyzer.build_report()

    print(report)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"📑 저장 완료: {report_path.relative_to(base_dir)}")
