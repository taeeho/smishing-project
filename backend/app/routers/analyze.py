"""
분석 API 라우터
통합 분석, 이미지 분석, URL 분석, 텍스트 분석, 이력 조회
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Query
import base64
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeTextRequest,
    AnalyzeUrlRequest,
    FAQItem,
    SourceItem,
    UrlAnalysisDetail,
    HistoryResponse,
    HistoryItem,
)
from app.db.schemas.trend import TrendResponse, TrendItem
from app.db.database import get_db
from app.service.pipeline import PipelineInput, run_pipeline
from app.core.security import decode_token
from app.db.models.message import Message
from app.db.models.url import Url
from app.db.models.analysis_result import AnalysisResult
from app.db.models.user import User

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
security = HTTPBearer()


async def _get_current_user_id(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession,
) -> int:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access 토큰이 아닙니다.")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰 정보가 올바르지 않습니다.")
    return int(user_id)


def _age_group_filter(age: int | None) -> str:
    if age is None:
        return "미공개"
    if 10 <= age <= 19:
        return "10대"
    if 20 <= age <= 29:
        return "20대"
    if 30 <= age <= 39:
        return "30대"
    if 40 <= age <= 49:
        return "40대"
    return "미공개"


async def _pipeline_to_response(input_type: str, pipeline_result, db: AsyncSession, user_id: int | None) -> AnalyzeResponse:
    """파이프라인 결과를 API 응답으로 변환합니다."""
    pr = pipeline_result
    rag = pr.rag_result

    # URL 분석 상세
    url_analyses = []
    for sb in pr.safebrowsing_results:
        ml = next((m for m in pr.ml_url_results if m.url == sb.url), None)
        url_analyses.append(UrlAnalysisDetail(
            url=sb.url,
            is_safe=sb.is_safe,
            threat_type=sb.threat_type,
            risk_score=ml.risk_score if ml else (90.0 if not sb.is_safe else 0.0),
            risk_label=ml.risk_label if ml else ("높음" if not sb.is_safe else "낮음"),
        ))
    # ML만 있는 URL 추가
    sb_urls = {sb.url for sb in pr.safebrowsing_results}
    for ml in pr.ml_url_results:
        if ml.url not in sb_urls:
            url_analyses.append(UrlAnalysisDetail(
                url=ml.url, is_safe=True,
                risk_score=ml.risk_score, risk_label=ml.risk_label,
            ))

    max_risk = max((u.risk_score for u in url_analyses), default=0.0)

    response = AnalyzeResponse(
        input_type=input_type,
        extracted_text=pr.extracted_text,
        extracted_urls=pr.extracted_urls,
        smishing_type=pr.bert_result.smishing_type if pr.bert_result else "판별불가",
        smishing_confidence=pr.bert_result.confidence if pr.bert_result else 0.0,
        url_analyses=url_analyses,
        max_url_risk_score=max_risk,
        url_risk_label=(
            "높음" if max_risk >= 70 else
            "중간" if max_risk >= 40 else
            "낮음" if url_analyses else "정보 부족"
        ),
        group_risk=pr.group_risk,
        risk_summary=rag.risk_summary if rag else "",
        evidence=rag.evidence if rag else [],
        recommended_actions=rag.recommended_actions if rag else [],
        report_template=rag.report_template if rag else "",
        report_procedure=rag.report_procedure if rag else "",
        guardian_summary=rag.guardian_summary if rag else "",
        coaching_steps=rag.coaching_steps if rag else [],
        faq=[FAQItem(**f) for f in rag.faq] if rag else [],
        similar_cases=rag.similar_cases if rag else "",
        sources=[SourceItem(title=s.title, source=s.source, snippet=s.snippet) for s in rag.sources] if rag else [],
        pipeline_steps=pr.pipeline_steps,
    )
    if user_id is not None:
        msg = Message(
            user_id=user_id,
            input_type=input_type,
            masked_text=(pr.extracted_text[:300] if pr.extracted_text else None),
            extracted_url=(pr.extracted_urls[0] if pr.extracted_urls else None),
        )
        db.add(msg)
        await db.flush()

        url_obj = None
        if pr.extracted_urls:
            first_url = pr.extracted_urls[0]
            url_obj = Url(
                msg_id=msg.msg_id,
                url_domain=first_url,
                safe_browsing_result="위험" if response.url_risk_label == "높음" else "안전",
                ml_risk_score=response.max_url_risk_score,
            )
            db.add(url_obj)
            await db.flush()

        analysis = AnalysisResult(
            msg_id=msg.msg_id,
            urls_id=url_obj.urls_id if url_obj else None,
            smishing_type=response.smishing_type,
            risk_score=response.max_url_risk_score,
            keywords=",".join(response.evidence[:2]) if response.evidence else None,
        )
        db.add(analysis)
        await db.commit()
    return response


@router.post("/", response_model=AnalyzeResponse)
async def analyze(
    payload: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AnalyzeResponse:
    """통합 분석 엔드포인트"""
    pipe_input = PipelineInput(
        input_type=payload.input_type,
        text=payload.text,
        image_base64=payload.image_base64,
        url=payload.url,
    )
    result = await run_pipeline(pipe_input, db)
    user_id = await _get_current_user_id(credentials, db)
    return await _pipeline_to_response(payload.input_type, result, db, user_id)


@router.post("/image", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """이미지 업로드 분석"""
    contents = await file.read()
    b64 = base64.b64encode(contents).decode("utf-8")
    pipe_input = PipelineInput(input_type="image", image_base64=b64)
    result = await run_pipeline(pipe_input, db)
    user_id = await _get_current_user_id(credentials, db)
    return await _pipeline_to_response("image", result, db, user_id)


@router.post("/url", response_model=AnalyzeResponse)
async def analyze_url(
    payload: AnalyzeUrlRequest,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AnalyzeResponse:
    """URL 직접 분석"""
    pipe_input = PipelineInput(input_type="url", url=payload.url)
    result = await run_pipeline(pipe_input, db)
    user_id = await _get_current_user_id(credentials, db)
    return await _pipeline_to_response("url", result, db, user_id)


@router.post("/text", response_model=AnalyzeResponse)
async def analyze_text(
    payload: AnalyzeTextRequest,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AnalyzeResponse:
    """텍스트 직접 분석"""
    pipe_input = PipelineInput(input_type="text", text=payload.text)
    result = await run_pipeline(pipe_input, db)
    user_id = await _get_current_user_id(credentials, db)
    return await _pipeline_to_response("text", result, db, user_id)


@router.get("/history", response_model=HistoryResponse)
async def analyze_history(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """분석 이력 조회"""
    user_id = await _get_current_user_id(credentials, db)
    result = await db.execute(
        select(AnalysisResult, Message)
        .join(Message, AnalysisResult.msg_id == Message.msg_id)
        .where(Message.user_id == user_id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(50)
    )
    rows = result.all()
    items: list[HistoryItem] = []
    for ar, msg in rows:
        status = "위험" if (ar.risk_score or 0) >= 70 else "안전"
        items.append(HistoryItem(
            analysis_id=ar.analysis_id,
            title=msg.masked_text[:20] + "..." if msg.masked_text else msg.extracted_url or "",
            status=status,
            risk_score=ar.risk_score or 0.0,
            created_at=str(ar.created_at),
        ))
    return HistoryResponse(total=len(items), results=items)


@router.get("/trends", response_model=TrendResponse)
async def analyze_trends(
    age_group: str = Query("미공개", description="10대 | 20대 | 30대 | 40대 | 미공개"),
    db: AsyncSession = Depends(get_db),
):
    """전체 사용자 기반 트렌드 집계 (최근 1년, Top 10)"""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)

    stmt = (
        select(AnalysisResult.smishing_type, func.count(AnalysisResult.analysis_id))
        .select_from(AnalysisResult)
        .join(Message, AnalysisResult.msg_id == Message.msg_id)
        .join(User, Message.user_id == User.user_id)
        .where(AnalysisResult.created_at >= start)
        .group_by(AnalysisResult.smishing_type)
    )

    if age_group != "미공개":
        # 나이대 필터링
        if age_group == "10대":
            stmt = stmt.where(User.age.between(10, 19))
        elif age_group == "20대":
            stmt = stmt.where(User.age.between(20, 29))
        elif age_group == "30대":
            stmt = stmt.where(User.age.between(30, 39))
        elif age_group == "40대":
            stmt = stmt.where(User.age.between(40, 49))
        else:
            stmt = stmt.where(User.age.is_(None))
    else:
        stmt = stmt.where(User.age.is_(None))

    stmt = stmt.order_by(func.count(AnalysisResult.analysis_id).desc()).limit(10)
    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return TrendResponse(
            age_group=age_group,
            start_date=start.date().isoformat(),
            end_date=now.date().isoformat(),
            results=[],
        )

    max_count = max((count for _, count in rows), default=1)
    items: list[TrendItem] = []
    for smishing_type, count in rows:
        label = smishing_type or "기타"
        similarity = round((count / max_count) * 100, 1)
        items.append(TrendItem(label=label, count=int(count), similarity=similarity))

    return TrendResponse(
        age_group=age_group,
        start_date=start.date().isoformat(),
        end_date=now.date().isoformat(),
        results=items,
    )
