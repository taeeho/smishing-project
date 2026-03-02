from datetime import datetime
from pydantic import BaseModel, Field


class GuardianCase(BaseModel):
    """보호자용 케이스"""
    case_id: int
    smishing_type: str = "미분류"
    risk_level: str = "정보 부족"
    summary: str = ""
    guardian_summary: str = ""
    status: str = "미조치"   # 미조치 | 확인중 | 완료
    memo: str = ""
    created_at: str = ""


class GuardianCaseList(BaseModel):
    """케이스 목록 응답"""
    total: int = 0
    cases: list[GuardianCase] = []
    unresolved_count: int = 0


class GuardianMemoRequest(BaseModel):
    """메모 추가 요청"""
    case_id: int
    memo: str = Field(..., max_length=500)


class GuardianStatusUpdate(BaseModel):
    """조치 상태 업데이트"""
    status: str = Field(..., description="미조치 | 확인중 | 완료")


class GuardianDailySummary(BaseModel):
    """하루 요약"""
    date: str
    total_cases: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    unresolved_count: int = 0
    summary_text: str = ""


class GuardianAlert(BaseModel):
    """보호자 알림"""
    alert_type: str = "위험"  # 위험 | 요약
    message: str = ""
    case_id: int | None = None
    created_at: str = ""
