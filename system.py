# system.py

# --- 지장간 정의 ---
HIDDEN = {
    '子': ['癸'],
    '丑': ['己','癸','辛'],
    '寅': ['甲','丙','戊'],
    '卯': ['乙'],
    '辰': ['戊','乙','癸'],
    '巳': ['丙','戊','庚'],
    '午': ['丁','己'],
    '未': ['己','乙','丁'],
    '申': ['庚','壬','戊'],
    '酉': ['辛'],
    '戌': ['戊','辛','丁'],
    '亥': ['壬','甲'],
}

# --- 천간 5합 ---
TG_HE = [
    ('甲','己','土'),
    ('乙','庚','金'),
    ('丙','辛','水'),
    ('丁','壬','木'),
    ('戊','癸','火'),
]

BRANCH_REL = {
    "충": [('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')],
    "형": [('寅','巳'),('丑','戌'),('戌','未')],
    "파": [('子','卯'),('午','卯'),('午','酉')],
    "천": [('寅','巳'),('申','亥'),('午','丑'),('子','未')],
}

SAMHAP = [
    (['申','子','辰'], "水局"),
    (['寅','午','戌'], "火局"),
    (['巳','酉','丑'], "金局"),
    (['亥','卯','未'], "木局"),
]

YUKHAP = {
    ('子','丑'):"水合", ('寅','亥'):"木合", ('卯','戌'):"火合",
    ('辰','酉'):"金合", ('巳','申'):"水合", ('午','未'):"土合"
}

def _has_tg_he(a_hiddens, b_hiddens):
    hits = []
    for x,y,res in TG_HE:
        if (x in a_hiddens and y in b_hiddens) or (y in a_hiddens and x in b_hiddens):
            hits.append((x+y, res))
    return hits

class SajuAnalyzer:
    def __init__(self, saju_input: str):
        self.saju = saju_input.split()
        self.branches = [p[1] for p in self.saju if len(p)==2]

    def check_relations(self):
        results = []
        for t, pairs in BRANCH_REL.items():
            for a,b in pairs:
                if a in self.branches and b in self.branches:
                    results.append(f"{a}{t}{b}")
        return results

    def check_samhap(self):
        results = []
        for group, label in SAMHAP:
            cnt = sum([1 for g in group if g in self.branches])
            if cnt == 3:
                results.append(f"삼합 {label} 완성 ({''.join(group)})")
            elif cnt == 2:
                results.append(f"삼합 {label} 부분 성립 ({''.join(group)})")
        return results

    def check_yukhap(self):
        results = []
        for (a,b),label in YUKHAP.items():
            if a in self.branches and b in self.branches:
                results.append(f"육합 {a}{b} = {label}")
        return results

    def check_am_hap(self, mode='loose'):
        results = []
        brs = list(dict.fromkeys([b for b in self.branches if b in HIDDEN]))
        for i in range(len(brs)):
            for j in range(i+1, len(brs)):
                a, b = brs[i], brs[j]
                a_h = [HIDDEN[a][0]] if mode=='strict' else HIDDEN[a]
                b_h = [HIDDEN[b][0]] if mode=='strict' else HIDDEN[b]
                hits = _has_tg_he(a_h, b_h)
                for pair,res in hits:
                    results.append(f"암합 {a}+{b}: 지장간 {pair} → {res}合")
        return results

    def analyze(self):
        result = {"입력": self.saju}
        result["합충형파천"] = self.check_relations()
        result["삼합"] = self.check_samhap()
        result["육합"] = self.check_yukhap()
        result["암합"] = self.check_am_hap()
        result["총평"] = "구조 분석 (합/충/형/파/천/삼합/육합/암합 포함)"
        return result
