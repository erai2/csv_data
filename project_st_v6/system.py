# saju_system.py
from collections import defaultdict

# 관계 세트
CHONG = {('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')}
HAP   = {('子','丑'),('寅','亥'),('卯','戌'),('巳','申'),('午','未')}
PO    = {('子','酉'),('卯','午'),('寅','亥'),('未','戌')}
CHUAN = {('子','未'),('丑','午'),('寅','巳'),('申','亥')}

WUXING = {"甲":"목","乙":"목","丙":"화","丁":"화","戊":"토","己":"토","庚":"금","辛":"금","壬":"수","癸":"수",
          "子":"수","丑":"토","寅":"목","卯":"목","辰":"토","巳":"화","午":"화","未":"토","申":"금","酉":"금","戌":"토","亥":"수"}

class HeavenlyStem:
    def __init__(self,name,ohaeng,yinyang):
        self.name=name; self.ohaeng=ohaeng; self.yinyang=yinyang

class EarthlyBranch:
    def __init__(self,name,ohaeng,yinyang,gijeong):
        self.name=name; self.ohaeng=ohaeng; self.yinyang=yinyang; self.gijeong=gijeong

class Pillar:
    def __init__(self,stem,branch,gungwi=None):
        self.stem=stem; self.branch=branch; self.gungwi=gungwi
    def __repr__(self): return f"{self.stem.name}{self.branch.name}주"

class Saju:
    def __init__(self,year,month,day,time,gungwi_mgr):
        self.year=year; self.month=month; self.day=day; self.time=time
        self.year.gungwi=gungwi_mgr.get_gungwi("년주")
        self.month.gungwi=gungwi_mgr.get_gungwi("월주")
        self.day.gungwi=gungwi_mgr.get_gungwi("일주")
        self.time.gungwi=gungwi_mgr.get_gungwi("시주")
    def get_pillars(self): return [self.year,self.month,self.day,self.time]

class Shishin: 
    def __init__(self,name,description,relations=None): 
        self.name=name; self.description=description; self.relations=relations or {}

class Gungwi:
    def __init__(self,name,life_stage,representative_kin,symbolic_meaning):
        self.name=name; self.life_stage=life_stage; self.representative_kin=representative_kin; self.symbolic_meaning=symbolic_meaning

class ShishinManager:
    def __init__(self,data): self._map={n:Shishin(n,i['description'],i.get('relations')) for n,i in data.items()}
    def get_shishin(self,n): return self._map.get(n)

class GungwiManager:
    def __init__(self,data): self._map={n:Gungwi(n,i['life_stage'],i['representative_kin'],i['symbolic_meaning']) for n,i in data.items()}
    def get_gungwi(self,n): return self._map.get(n)

class SajuAnalyzer:
    def __init__(self,saju,shishin_mgr,parsed_data=None):
        self.saju=saju; self.shishin_mgr=shishin_mgr; self.parsed_data=parsed_data or {}

    def analyze_gungwi(self):
        lines=["--- 궁위 분석 ---"]
        for p in self.saju.get_pillars():
            if p.gungwi:
                lines.append(f"{p} → {p.gungwi.symbolic_meaning} ({p.gungwi.life_stage})")
        return "\n".join(lines)

    def analyze_sipsin(self):
        lines=["--- 십신 분석 ---"]
        ilgan=self.saju.day.stem
        for p in self.saju.get_pillars():
            if p.stem.name==ilgan.name:
                lines.append(f"{p}: 일간")
            else:
                lines.append(f"{p}: 기타")
        return "\n".join(lines)

    def analyze_branch_relations(self):
        lines=["--- 지지 관계 ---"]
        br=[p.branch.name for p in self.saju.get_pillars()]
        for i in range(len(br)):
            for j in range(i+1,len(br)):
                a,b=br[i],br[j]
                if (a,b) in CHONG or (b,a) in CHONG: lines.append(f"{a}-{b}: 충")
                if (a,b) in HAP or (b,a) in HAP: lines.append(f"{a}-{b}: 합")
                if (a,b) in PO or (b,a) in PO: lines.append(f"{a}-{b}: 파")
                if (a,b) in CHUAN or (b,a) in CHUAN: lines.append(f"{a}-{b}: 천")
        return "\n".join(lines)

    def analyze_advanced_rules(self):
        lines=["--- 고급 규칙 ---"]
        for p in self.saju.get_pillars():
            s,b=p.stem.name,p.branch.name
            if WUXING.get(s)==WUXING.get(b): lines.append(f"{s}{b}: 실")
            else: lines.append(f"{s}{b}: 허")
        return "\n".join(lines)

    def analyze_with_rules(self):
        lines=["--- 문헌 규칙 기반 분석 ---"]
        for k,v in self.parsed_data.items():
            lines.append(f"▶ {k} 규칙")
            for r in v: lines.append(f" - {r['rule']} (출처 {r['file']})")
        return "\n".join(lines)

    def analyze_unse(self,daewoon,sewun):
        lines=["--- 대운·세운 응기 분석 ---"]
        # 대운
        lines.append(f"▶ 대운: {daewoon['stem']}{daewoon['branch']}")
        if (daewoon['branch'],self.saju.day.branch.name) in CHONG: lines.append(" - 대운이 일지와 충 → 혼인/가정 불안정")
        if (daewoon['branch'],self.saju.day.branch.name) in HAP: lines.append(" - 대운이 일지와 합 → 혼인/인연")
        # 세운
        lines.append(f"▶ 세운: {sewun['stem']}{sewun['branch']}")
        if (sewun['branch'],self.saju.day.branch.name) in CHONG: lines.append(" - 세운이 일지와 충 → 사건 발생")
        if (sewun['branch'],self.saju.day.branch.name) in HAP: lines.append(" - 세운이 일지와 합 → 혼인/연애 사건")
        return "\n".join(lines)
