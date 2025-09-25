# saju_loader.py
import json
from system import ShishinManager,GungwiManager

def load_parsed_data(json_file="parsed_all.json"):
    data=json.load(open(json_file,encoding="utf-8"))
    shishin_mgr=ShishinManager({"비견":{"description":"자아"},"겁재":{"description":"투쟁"}})
    gungwi_mgr=GungwiManager({
        "년주":{"life_stage":"유년","representative_kin":"조상","symbolic_meaning":"해외"},
        "월주":{"life_stage":"청년","representative_kin":"부모","symbolic_meaning":"본적"},
        "일주":{"life_stage":"장년","representative_kin":"배우자","symbolic_meaning":"자아"},
        "시주":{"life_stage":"말년","representative_kin":"자식","symbolic_meaning":"출구"},
    })
    return data,shishin_mgr,gungwi_mgr
