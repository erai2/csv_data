# saju_system.py
import json
from collections import defaultdict

# === (1) 기본 데이터 ===
HEAVENLY_STEMS = {
    '甲': {'ohaeng': '목', 'yinyang': '양'}, '乙': {'ohaeng': '목', 'yinyang': '음'},
    '丙': {'ohaeng': '화', 'yinyang': '양'}, '丁': {'ohaeng': '화', 'yinyang': '음'},
    '戊': {'ohaeng': '토', 'yinyang': '양'}, '己': {'ohaeng': '토', 'yinyang': '음'},
    '庚': {'ohaeng': '금', 'yinyang': '양'}, '辛': {'ohaeng': '금', 'yinyang': '음'},
    '壬': {'ohaeng': '수', 'yinyang': '양'}, '癸': {'ohaeng': '수', 'yinyang': '음'},
}
EARTHLY_BRANCHES = {
    '子': {'ohaeng': '수', 'yinyang': '양'},
    '丑': {'ohaeng': '토', 'yinyang': '음'},
    '寅': {'ohaeng': '목', 'yinyang': '양'},
    '卯': {'ohaeng': '목', 'yinyang': '음'},
    '辰': {'ohaeng': '토', 'yinyang': '양'},
    '巳': {'ohaeng': '화', 'yinyang': '음'},
    '午': {'ohaeng': '화', 'yinyang': '양'},
    '未': {'ohaeng': '토', 'yinyang': '음'},
    '申': {'ohaeng': '금', 'yinyang': '양'},
    '酉': {'ohaeng': '금', 'yinyang': '음'},
    '戌': {'ohaeng': '토', 'yinyang': '양'},
    '亥': {'ohaeng': '수', 'yinyang': '음'},
}

# === (2) 클래스 정의 ===
class HeavenlyStem:
    def __init__(self, name):
        self.name = name
        self.ohaeng = HEAVENLY_STEMS[name]["ohaeng"]
        self.yinyang = HEAVENLY_STEMS[name]["yinyang"]
    def __repr__(self):
        return f"천간({self.name})"

class EarthlyBranch:
    def __init__(self, name):
        self.name = name
        self.ohaeng = EARTHLY_BRANCHES[name]["ohaeng"]
        self.yinyang = EARTHLY_BRANCHES[name]["yinyang"]
    def __repr__(self):
        return f"지지({self.name})"

class Pillar:
    def __init__(self, stem, branch):
        self.stem = HeavenlyStem(stem)
        self.branch = EarthlyBranch(branch)
    def __repr__(self):
        return f"{self.stem.name}{self.branch.name}주"

class Saju:
    def __init__(self, year, month, day, time):
        self.year = year
        self.month = month
        self.day = day
        self.time = time
    def get_pillars(self):
        return [self.year, self.month, self.day, self.time]
    def __repr__(self):
        return f"사주: {self.year}, {self.month}, {self.day}, {self.time}"

# === (3) Analyzer ===
class SajuAnalyzer:
    def __init__(self, saju=None, parsed_data_path="parsed_all.json"):
        self.saju = saju
        self.parsed_data_path = parsed_data_path
        self.parsed_data = self._load_parsed_data()

    def _load_parsed_data(self):
        try:
            with open(self.parsed_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def analyze_gungwi(self):
        if not self.saju:
            return "⚠️ 사주 데이터 없음"
        lines = ["--- 궁위 분석 ---"]
        for p in self.saju.get_pillars():
            lines.append(str(p))
        return "\n".join(lines)

    def summarize_by_category(self):
        cats = defaultdict(list)
        for fname, doc in self.parsed_data.items():
            for para in doc.get("rules", []):
                cats[para["category"]].append(para["content"])

        lines = ["--- 규칙별 요약 ---"]
        for cat, items in cats.items():
            lines.append(f"\n[{cat}] ({len(items)}개)")
            for i, txt in enumerate(items[:5], 1):  # 최대 5개 미리보기
                lines.append(f"{i}. {txt}")
        return "\n".join(lines)

    def build_report(self):
        report = []
        report.append("=== 사주 분석 리포트 ===")
        if self.saju:
            report.append(f"\n[사주 구조]\n{self.saju}")
        report.append("\n" + self.analyze_gungwi())
        report.append("\n" + self.summarize_by_category())
        return "\n".join(report)
