"""
보호자 모드 API 라우터
케이스 목록, 메모, 상태 업데이트, 하루 요약
"""
from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter

from app.db.schemas.guardian import (
    GuardianAlert,
    GuardianCase,
    GuardianCaseList,
    GuardianDailySummary,
    GuardianMemoRequest,
    GuardianStatusUpdate,
)

router = APIRouter(prefix="/api/guardian", tags=["guardian"])

# ── 인메모리 저장소 (시뮬레이션) ─────────────────────────────
# 실제 배포 시 DB 연동으로 교체합니다.
_cases: dict[int, dict] = {
    1: {
        "case_id": 1,
        "smishing_type": "택배사칭",
        "risk_level": "높음",
        "summary": "CJ대한통운 사칭 택배 배송 확인 문자",
        "guardian_summary": "⚠️ 스미싱 의심 (택배사칭) | 위험도: 높음. 링크 클릭·송금 중단 필요.",
        "status": "미조치",
        "memo": "",
        "created_at": "2026-02-27T10:30:00",
    },
    2: {
        "case_id": 2,
        "smishing_type": "기관사칭",
        "risk_level": "중간",
        "summary": "국민건강보험 건강검진 결과 확인 문자",
        "guardian_summary": "⚠️ 스미싱 의심 (기관사칭) | 위험도: 중간. 공식 채널 확인 요망.",
        "status": "확인중",
        "memo": "어머니께 전화로 확인 완료",
        "created_at": "2026-02-26T14:15:00",
    },
}
_next_id = 3


@router.get("/cases", response_model=GuardianCaseList)
async def get_cases():
    """보호자용 케이스 목록 조회"""
    cases = [GuardianCase(**c) for c in _cases.values()]
    cases.sort(key=lambda c: c.created_at, reverse=True)
    unresolved = sum(1 for c in cases if c.status != "완료")
    return GuardianCaseList(
        total=len(cases),
        cases=cases,
        unresolved_count=unresolved,
    )


@router.post("/memo")
async def add_memo(req: GuardianMemoRequest):
    """케이스에 메모 추가"""
    if req.case_id not in _cases:
        return {"error": "케이스를 찾을 수 없습니다.", "case_id": req.case_id}
    _cases[req.case_id]["memo"] = req.memo
    return {"message": "메모가 저장되었습니다.", "case_id": req.case_id}


@router.patch("/case/{case_id}/status")
async def update_status(case_id: int, req: GuardianStatusUpdate):
    """조치 상태 업데이트"""
    if case_id not in _cases:
        return {"error": "케이스를 찾을 수 없습니다.", "case_id": case_id}
    if req.status not in ("미조치", "확인중", "완료"):
        return {"error": "유효하지 않은 상태입니다.", "valid": ["미조치", "확인중", "완료"]}
    _cases[case_id]["status"] = req.status
    return {"message": f"상태가 '{req.status}'로 변경되었습니다.", "case_id": case_id}


@router.get("/summary", response_model=GuardianDailySummary)
async def daily_summary():
    """하루 요약"""
    today = datetime.now().strftime("%Y-%m-%d")
    cases = list(_cases.values())
    high = sum(1 for c in cases if c["risk_level"] == "높음")
    medium = sum(1 for c in cases if c["risk_level"] == "중간")
    low = sum(1 for c in cases if c["risk_level"] == "낮음")
    unresolved = sum(1 for c in cases if c["status"] != "완료")

    summary_text = f"오늘 {len(cases)}건의 분석이 진행되었습니다. "
    if high > 0:
        summary_text += f"위험 {high}건, "
    if medium > 0:
        summary_text += f"주의 {medium}건, "
    if low > 0:
        summary_text += f"안전 {low}건. "
    if unresolved > 0:
        summary_text += f"미조치 {unresolved}건이 남아있습니다."

    return GuardianDailySummary(
        date=today,
        total_cases=len(cases),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        unresolved_count=unresolved,
        summary_text=summary_text.strip(),
    )


@router.get("/alerts")
async def get_alerts():
    """보호자 알림 목록"""
    alerts = []
    for c in _cases.values():
        if c["risk_level"] == "높음" and c["status"] != "완료":
            alerts.append(GuardianAlert(
                alert_type="위험",
                message=c["guardian_summary"],
                case_id=c["case_id"],
                created_at=c["created_at"],
            ))
    return {"alerts": [a.model_dump() for a in alerts]}
