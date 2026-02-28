"""
분석 API 라우터
통합 분석, 이미지 분석, URL 분석, 텍스트 분석, 이력 조회
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, Depends
import base64
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeTextRequest,
    AnalyzeUrlRequest,
    FAQItem,
    SourceItem,
    UrlAnalysisDetail,
)
from app.db.database import get_db
from app.service.pipeline import PipelineInput, run_pipeline

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


def _pipeline_to_response(input_type: str, pipeline_result) -> AnalyzeResponse:
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

    return AnalyzeResponse(
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


@router.post("/", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest, db: AsyncSession = Depends(get_db)) -> AnalyzeResponse:
    """통합 분석 엔드포인트"""
    pipe_input = PipelineInput(
        input_type=payload.input_type,
        text=payload.text,
        image_base64=payload.image_base64,
        url=payload.url,
    )
    result = await run_pipeline(pipe_input, db)
    return _pipeline_to_response(payload.input_type, result)


@router.post("/image", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """이미지 업로드 분석"""
    contents = await file.read()
    b64 = base64.b64encode(contents).decode("utf-8")
    pipe_input = PipelineInput(input_type="image", image_base64=b64)
    result = await run_pipeline(pipe_input, db)
    return _pipeline_to_response("image", result)


@router.post("/url", response_model=AnalyzeResponse)
async def analyze_url(payload: AnalyzeUrlRequest, db: AsyncSession = Depends(get_db)) -> AnalyzeResponse:
    """URL 직접 분석"""
    pipe_input = PipelineInput(input_type="url", url=payload.url)
    result = await run_pipeline(pipe_input, db)
    return _pipeline_to_response("url", result)


@router.post("/text", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeTextRequest, db: AsyncSession = Depends(get_db)) -> AnalyzeResponse:
    """텍스트 직접 분석"""
    pipe_input = PipelineInput(input_type="text", text=payload.text)
    result = await run_pipeline(pipe_input, db)
    return _pipeline_to_response("text", result)


@router.get("/history")
async def analyze_history():
    """분석 이력 조회 (시뮬레이션)"""
    # TODO: DB에서 실제 이력을 조회
    return {
        "total": 0,
        "results": [],
        "message": "분석 이력이 없습니다. 분석을 실행해 주세요.",
    }
