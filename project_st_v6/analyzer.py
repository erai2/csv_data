# saju_analyzer.py
import json
from collections import defaultdict

class SajuAnalyzer:
    def __init__(self, saju=None, shishin_manager=None, parsed_data_path="parsed_all.json"):
        self.saju = saju
        self.shishin_manager = shishin_manager
        self.parsed_data_path = parsed_data_path
        self.parsed_data = self._load_parsed_data()

    def _load_parsed_data(self):
        try:
            with open(self.parsed_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ parsed_all.json 파일을 찾을 수 없습니다.")
            return {}

    # === 카테고리별 집계 ===
    def summarize_by_category(self):
        summary = defaultdict(list)

        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                cat = para.get("category", "unknown")
                summary[cat].append(para["content"])

        result = []
        result.append("=== 카테고리별 요약 ===")

        for cat, paras in summary.items():
            result.append(f"\n[{cat.upper()}] ({len(paras)}개)")
            for i, p in enumerate(paras[:5], 1):  # 미리보기 5개
                preview = p[:120].replace("\n", " ")
                result.append(f"{i}. {preview}...")

        return "\n".join(result)

    # === 규칙 모아 리포트 ===
    def extract_rules(self):
        rules = []
        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                if para.get("category") == "rule":
                    rules.append(para["content"])
        return "\n".join(rules)

    # === 사례 모아 리포트 ===
    def extract_cases(self):
        cases = []
        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                if para.get("category") == "case":
                    cases.append(para["content"])
        return "\n".join(cases)

    # === 개념 모아 리포트 ===
    def extract_concepts(self):
        concepts = []
        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                if para.get("category") == "concept":
                    concepts.append(para["content"])
        return "\n".join(concepts)

    # === 전체 리포트 ===
    def build_report(self):
        report = []
        report.append("=== 사주 분석 + 문헌 리포트 ===")

        # 원국/사주 해석 (옵션)
        if self.saju:
            report.append(f"\n[사주 구조]\n{saju}")

        # 카테고리별 요약
        report.append("\n" + self.summarize_by_category())

        # 규칙/사례/개념 전문
        report.append("\n[규칙 전체]\n" + self.extract_rules())
        report.append("\n[사례 전체]\n" + self.extract_cases())
        report.append("\n[개념 전체]\n" + self.extract_concepts())

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = SajuAnalyzer()
    text_report = analyzer.build_report()

    # 결과 저장
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(text_report)

    print("✅ 분석 리포트 생성 완료 → analysis_report.md")
