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
WUXING = {**{k: v['ohaeng'] for k, v in HEAVENLY_STEMS.items()},
          **{k: v['ohaeng'] for k, v in EARTHLY_BRANCHES.items()}}

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

class Shishin:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def __repr__(self):
        return f"십신({self.name})"

class Gungwi:
    def __init__(self, name, life_stage, representative_kin, symbolic_meaning):
        self.name = name
        self.life_stage = life_stage
        self.representative_kin = representative_kin
        self.symbolic_meaning = symbolic_meaning
    def __repr__(self):
        return f"궁위({self.name})"

class ShishinManager:
    def __init__(self, data):
        self._shishins = {name: Shishin(name, info["description"]) for name, info in data.items()}
    def get(self, name):
        return self._shishins.get(name)

class GungwiManager:
    def __init__(self, data):
        self._gungwis = {name: Gungwi(name, **info) for name, info in data.items()}
    def get(self, name):
        return self._gungwis.get(name)

# === (3) Analyzer 확장 ===
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

    # 궁위
    def analyze_gungwi(self):
        if not self.saju:
            return "⚠️ 사주 데이터 없음"
        lines = ["--- 궁위 분석 ---"]
        for p in self.saju.get_pillars():
            lines.append(str(p))
        return "\n".join(lines)

    # 카테고리 요약
    def summarize_by_category(self):
        cats = {"rule": [], "case": [], "concept": []}
        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                cat = para.get("category", "unknown")
                if cat in cats:
                    cats[cat].append(para["content"])
        lines = ["--- 카테고리별 요약 ---"]
        for k, v in cats.items():
            lines.append(f"[{k.upper()}] {len(v)}개")
            for i, txt in enumerate(v[:3], 1):
                lines.append(f"{i}. {txt[:100]}...")
        return "\n".join(lines)

    # 규칙 상세 (Markdown 표)
    def analyze_rules(self):
        details = {}
        for fname, doc in self.parsed_data.items():
            for para in doc.get("paragraphs", []):
                if para["category"] == "rule" and para.get("rule_type"):
                    details.setdefault(para["rule_type"], []).append({
                        "file": fname,
                        "id": para["id"],
                        "content": para["content"]
                    })

        lines = ["--- 규칙 상세 (Markdown 표) ---"]
        for rule_type, items in details.items():
            lines.append(f"\n### {rule_type}")
            lines.append("| 파일 | ID | 내용 |")
            lines.append("|------|----|------|")
            for item in items:
                lines.append(f"| {item['file']} | {item['id']} | {item['content'].replace(chr(10), ' ')} |")
        return "\n".join(lines)

    # 사건화 조건
    def analyze_events(self):
        lines = ["--- 사건화 조건 ---"]
        lines.append("재물: 財星 + 庫開 + 合/沖")
        lines.append("직장: 官星 + 印星 → 官印相生格 or 帶象")
        lines.append("혼인: 夫宮·夫星 / 妻宮·妻星이 合·沖·刑·破·入墓")
        lines.append("자식: 子息宮·子息星이 入墓·庫開·穿倒")
        lines.append("부모: 年/月柱 印星·食神의 합/충/형/穿")
        return "\n".join(lines)

    # 대운/세운 응기
    def analyze_daeseun(self):
        lines = ["--- 대운·세운 응기 ---"]
        lines.append("▶ 대운: 10년 단위 → 천간 5년 / 지지 5년 분리")
        lines.append("▶ 세운: 대운의 씨앗을 현실로 발현 (합/충/형/파/천/입묘 필요)")
        lines.append("▶ 응기 사례:")
        lines.append("  - 혼인: 배우자궁 합 → 결혼, 入墓 → 이혼")
        lines.append("  - 승진: 官印相生格 성립 시")
        lines.append("  - 재물: 財星 + 庫開")
        return "\n".join(lines)

    def build_report(self):
        report = ["=== 사주 분석 리포트 ==="]
        if self.saju:
            report.append(f"[사주 구조]\n{self.saju}")
        report.append("\n" + self.analyze_gungwi())
        report.append("\n" + self.summarize_by_category())
        report.append("\n" + self.analyze_rules())
        report.append("\n" + self.analyze_events())
        report.append("\n" + self.analyze_daeseun())
        return "\n".join(report)
