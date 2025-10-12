from typing import Dict, List, Tuple


def analyze_chart(gan_str: str, zhi_str: str) -> Dict[str, List[str]]:
    gans = gan_str.split()
    zhis = zhi_str.split()
    pairs = [f"{g}{z}" for g, z in zip(gans, zhis)]

    relations: List[Tuple[str, str, str]] = []
    if "午" in zhis and "卯" in zhis:
        relations.append(("午", "卯", "破"))
    if "卯" in zhis and "亥" in zhis:
        relations.append(("卯", "亥", "合"))

    structure = {
        "천간": gans,
        "지지": zhis,
        "조합": pairs,
        "감지관계": relations,
    }
    return structure
