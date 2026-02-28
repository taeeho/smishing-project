"""집단 위험 분석 (시뮬레이션)"""
from __future__ import annotations


def check_group_risk(smishing_type: str | None, urls: list[str]) -> bool:
    """
    집단 패턴 분석 시뮬레이션
    실제 배포 시 DB에서 유사 신고 빈도를 조회합니다.
    """
    HIGH_FREQUENCY_TYPES = {"택배사칭", "기관사칭", "금융사기"}
    if smishing_type in HIGH_FREQUENCY_TYPES:
        return True
    if len(urls) >= 2:
        return True
    return False
