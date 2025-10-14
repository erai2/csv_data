"""Explainable inference rules for 명리 fortune analysis."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


def infer_logic_explainable(base: Dict[str, Any], daewoon: str, sewoon: str) -> List[Dict[str, Any]]:
    """Generate explainable interpretations enriched with principles."""

    relations: Sequence[str] = base.get("관계", [])
    geokguk: str = base.get("격국", "")
    focus: Sequence[str] = base.get("대상", [])

    results: List[Dict[str, Any]] = []

    # 혼인 해석
    if any(rel for rel in relations if "破" in rel or "合去" in rel):
        results.append(
            {
                "분야": "혼인",
                "결과": "관계 단절 / 재혼 가능",
                "원리": (
                    "夫宮의 破 또는 合去는 배우자궁 파괴·합거를 의미합니다. "
                    "다만 새로운 合이 유입되면 재혼 작용으로 전환될 여지가 큽니다."
                ),
                "근거": [rel for rel in relations if "破" in rel or "合" in rel],
            }
        )

    # 직업 해석
    if geokguk in {"官印相生格", "食神生財格"}:
        results.append(
            {
                "분야": "직업",
                "결과": "명예·관직형 / 창의직 가능",
                "원리": (
                    f"{geokguk} 구조는 體가 用을 생하여 사회적·직업적 성취를 뒷받침합니다. "
                    "印이 관을 돕거나 食神이 財를 생하여 실무와 명예가 조화됩니다."
                ),
                "근거": geokguk,
            }
        )

    # 재물 해석
    if any("財" in rel for rel in relations) or any("財" in item for item in focus):
        results.append(
            {
                "분야": "재물",
                "결과": "재물운 상승",
                "원리": (
                    "財庫開는 재성의 저장고가 열려 현실적 이익이 커짐을 뜻합니다. "
                    "또한 財統官은 재물이 관성을 통제해 자원 운용 능력을 높입니다."
                ),
                "근거": [rel for rel in relations if "財" in rel] or list(focus),
            }
        )

    # 건강 해석
    if any(rel for rel in relations if "印破" in rel or "印沖" in rel):
        results.append(
            {
                "분야": "건강",
                "결과": "정신적 피로, 위장계 약화",
                "원리": (
                    "印은 보호·안정의 기운이지만 印破/沖이 발생하면 심신의 균형이 깨지고 "
                    "소화기와 면역계가 약화될 수 있습니다. 대운/세운의 충이 겹치면 더욱 주의가 필요합니다."
                ),
                "근거": [rel for rel in relations if "印" in rel],
            }
        )

    # 운세 보정
    if daewoon or sewoon:
        results.append(
            {
                "분야": "운세",
                "결과": "대운·세운 영향 참고",
                "원리": (
                    "현재 입력된 대운/세운은 구조 해석의 보조지표로 활용됩니다. "
                    "충·합 여부를 재확인하여 시기적 작용을 정밀하게 보정하세요."
                ),
                "근거": {"대운": daewoon, "세운": sewoon},
            }
        )

    if not results:
        results.append(
            {
                "분야": "일반",
                "결과": "안정적 흐름",
                "원리": "합·충·형·파 주요 작용이 없어 평온한 흐름으로 판단됩니다.",
                "근거": "무특이",
            }
        )

    return results

