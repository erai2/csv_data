# saju_runner.py
import os,json
from system import HeavenlyStem,EarthlyBranch,Pillar,Saju,ShishinManager,GungwiManager,SajuAnalyzer
from parser import parse_documents
from reportlab.platypus import SimpleDocTemplate,Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def save_report(text,name="analysis_report"):
    os.makedirs("reports",exist_ok=True)
    with open(f"reports/{name}.md","w",encoding="utf-8") as f:f.write(text)
    with open(f"reports/{name}.json","w",encoding="utf-8") as f:json.dump({"report":text},f,ensure_ascii=False,indent=2)
    pdf=SimpleDocTemplate(f"reports/{name}.pdf")
    style=getSampleStyleSheet()["Normal"]
    pdf.build([Paragraph(line,style) for line in text.split("\n")])

def run_analysis():
    parsed=parse_documents("docs")
    gungwi_mgr=GungwiManager({
        "년주":{"life_stage":"유년","representative_kin":"조상","symbolic_meaning":"해외"},
        "월주":{"life_stage":"청년","representative_kin":"부모","symbolic_meaning":"본적"},
        "일주":{"life_stage":"장년","representative_kin":"배우자","symbolic_meaning":"자아"},
        "시주":{"life_stage":"말년","representative_kin":"자식","symbolic_meaning":"출구"},
    })
    shishin_mgr=ShishinManager({"비견":{"description":"자아"},"겁재":{"description":"투쟁"}})
    year=Pillar(HeavenlyStem("丙","화","양"),EarthlyBranch("申","금","양",{}))
    month=Pillar(HeavenlyStem("丙","화","양"),EarthlyBranch("申","금","양",{}))
    day=Pillar(HeavenlyStem("辛","금","음"),EarthlyBranch("酉","금","음",{}))
    time=Pillar(HeavenlyStem("丁","화","음"),EarthlyBranch("未","토","음",{}))
    saju=Saju(year,month,day,time,gungwi_mgr)
    analyzer=SajuAnalyzer(saju,shishin_mgr,parsed)

    daewoon={"stem":"甲","branch":"子"}
    sewun={"stem":"乙","branch":"丑"}

    report=[]
    report.append("=== 사주 분석 리포트 ===")
    report.append(str(saju))
    report.append(analyzer.analyze_gungwi())
    report.append(analyzer.analyze_sipsin())
    report.append(analyzer.analyze_branch_relations())
    report.append(analyzer.analyze_advanced_rules())
    report.append(analyzer.analyze_with_rules())
    report.append(analyzer.analyze_unse(daewoon,sewun))
    text="\n".join(report)
    save_report(text)
    return text

if __name__=="__main__":
    print(run_analysis())
