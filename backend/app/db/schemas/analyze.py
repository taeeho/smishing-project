"""분석 API 관련 Pydantic 스키마"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# 요청 스키마
# ─────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """통합 분석 요청"""
    input_type: str = Field(
        default="text",
        description="입력 유형: text | image | url | qr",
    )
    text: str | None = Field(default=None, description="분석할 텍스트")
    image_base64: str | None = Field(default=None, description="Base64 인코딩 이미지")
    url: str | None = Field(default=None, description="분석할 URL")


class AnalyzeUrlRequest(BaseModel):
    """URL 직접 분석 요청"""
    url: str = Field(..., description="분석할 URL")


class AnalyzeTextRequest(BaseModel):
    """텍스트 직접 분석 요청"""
    text: str = Field(..., description="분석할 텍스트")


# ─────────────────────────────────────────────────────────────
# 응답 스키마
# ─────────────────────────────────────────────────────────────

class SourceItem(BaseModel):
    title: str
    source: str
    snippet: str


class FAQItem(BaseModel):
    q: str
    a: str


class UrlAnalysisDetail(BaseModel):
    url: str
    is_safe: bool
    threat_type: str | None = None
    risk_score: float = 0.0
    risk_label: str = "정보 부족"


class AnalyzeResponse(BaseModel):
    """통합 분석 응답"""
    # 입력 처리
    input_type: str
    extracted_text: str = ""
    extracted_urls: list[str] = []

    # BERT 분류
    smishing_type: str = "판별불가"
    smishing_confidence: float = 0.0

    # URL 분석
    url_analyses: list[UrlAnalysisDetail] = []
    max_url_risk_score: float = 0.0
    url_risk_label: str = "정보 부족"

    # 집단 패턴
    group_risk: bool = False

    # RAG 가이드
    risk_summary: str = ""
    evidence: list[str] = []
    recommended_actions: list[str] = []
    report_template: str = ""
    report_procedure: str = ""
    guardian_summary: str = ""
    coaching_steps: list[str] = []
    faq: list[FAQItem] = []
    similar_cases: str = ""

    # 메타
    sources: list[SourceItem] = []
    pipeline_steps: list[str] = []


class HistoryItem(BaseModel):
    analysis_id: int
    title: str = ""
    status: str = "안전"
    risk_score: float = 0.0
    created_at: str = ""


class HistoryResponse(BaseModel):
    total: int = 0
    results: list[HistoryItem] = []
