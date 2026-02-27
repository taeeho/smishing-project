from app.db.schemas.coach import CoachInput, CoachOutput, CoachSource


def _score_label(score: float | None) -> str:
    if score is None:
        return "정보 부족"
    if score >= 80:
        return "높음"
    if score >= 50:
        return "중간"
    return "낮음"


def build_coach_output(payload: CoachInput) -> CoachOutput:
    score_label = _score_label(payload.url_risk_score)
    signals: list[str] = []

    if payload.smishing_type:
        signals.append(f"분류 유형: {payload.smishing_type}")
    if payload.url_domain:
        signals.append(f"의심 URL 도메인: {payload.url_domain}")
    if payload.url_risk_score is not None:
        signals.append(f"URL 위험도: {score_label}")
    if payload.group_risk is True:
        signals.append("동일 유형 신고가 늘고 있음")
    if payload.ner_entities:
        signals.append(f"주요 키워드: {', '.join(payload.ner_entities[:5])}")

    if not signals:
        signals.append("분석 신호가 부족함")

    risk_summary = (
        "사기일 가능성을 배제할 수 없어요. "
        f"현재 위험도는 {score_label} 수준으로 보여요."
    )

    recommended_actions = [
        "링크를 누르지 말고 화면을 캡처해 두세요.",
        "발신처 번호로 다시 전화하지 말고, 공식 고객센터로 확인하세요.",
        "문자 속 인증번호나 계좌번호는 보내지 마세요.",
        "같은 내용이 반복되면 차단하고 신고하세요.",
    ]

    report_template = (
        "의심 문자 신고\n"
        "수신 일시: [날짜/시간]\n"
        "문자 내용 요약: [요약]\n"
        "의심 링크: [있으면 입력]\n"
        "피해 여부: [미발생/발생]\n"
        "요청 사항: 분석 및 차단 요청"
    )

    guardian_summary = (
        "확정 판단은 어렵지만 위험 신호가 있어요. "
        "링크 클릭이나 송금은 중단하고, 공식 채널로 확인하도록 도와주세요."
    )

    sources = [
        CoachSource(
            title="내부 분석 결과",
            source="smishing-analyzer",
            snippet="분류 결과와 URL 위험도를 종합해 안내했습니다.",
        )
    ]

    return CoachOutput(
        risk_summary=risk_summary,
        evidence=signals,
        recommended_actions=recommended_actions,
        report_template=report_template,
        guardian_summary=guardian_summary,
        sources=sources,
    )
