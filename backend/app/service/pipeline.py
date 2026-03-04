from dataclasses import dataclass, field
from ai_ocr.ocr_service import ocr_from_base64, extract_urls_from_text, OCRResult
from app.service.qr_service import decode_qr_from_base64, QRResult
from ai_bert.bert_service import classify_text, BERTResult
from app.service.safebrowsing_service import check_urls, SafeBrowsingResult
from app.service.ml_url_service import score_urls, MLUrlResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ai_rag.rag_service import generate_guidance, RAGResult
from ai_group_risk.group_risk import check_group_risk
from app.core.settings import settings
from app.db.models.text_training import TextTrainingData
from app.db.models.url_training import UrlTrainingData



@dataclass
class PipelineInput:
    """파이프라인 입력"""
    input_type: str = "text"   # "text" | "image" | "url" | "qr"
    text: str | None = None
    image_base64: str | None = None
    url: str | None = None


@dataclass
class PipelineResult:
    """파이프라인 최종 결과"""
    ocr_result: OCRResult | None = None
    qr_result: QRResult | None = None
    extracted_text: str = ""
    extracted_urls: list[str] = field(default_factory=list)

    bert_result: BERTResult | None = None
    safebrowsing_results: list[SafeBrowsingResult] = field(default_factory=list)
    ml_url_results: list[MLUrlResult] = field(default_factory=list)

    group_risk: bool = False

    rag_result: RAGResult | None = None
    rag_engine: str = "fallback"
    rag_error: str | None = None

    pipeline_steps: list[str] = field(default_factory=list)


async def run_pipeline(input_data: PipelineInput, db: AsyncSession) -> PipelineResult:
    """
    전체 분석 파이프라인을 실행합니다.

    LangChain 교체 시:
        from langchain.chains import SequentialChain
        chain = SequentialChain(chains=[ocr_chain, bert_chain, url_chain, rag_chain])
        result = chain.run(input_data)
    """
    result = PipelineResult()

    result.pipeline_steps.append("입력 처리")

    if input_data.input_type == "image" and input_data.image_base64:
        result.ocr_result = ocr_from_base64(input_data.image_base64)
        result.extracted_text = result.ocr_result.raw_text
        result.extracted_urls = list(result.ocr_result.extracted_urls)
        result.pipeline_steps.append("OCR 텍스트 추출 완료")

        result.qr_result = decode_qr_from_base64(input_data.image_base64)
        if result.qr_result.success:
            result.extracted_urls.extend(result.qr_result.decoded_urls)
            result.pipeline_steps.append("QR 코드 디코딩 완료")

    elif input_data.input_type == "qr" and input_data.image_base64:
        result.qr_result = decode_qr_from_base64(input_data.image_base64)
        if result.qr_result.success:
            result.extracted_urls = list(result.qr_result.decoded_urls)
            result.pipeline_steps.append("QR 코드 디코딩 완료")

    elif input_data.input_type == "url" and input_data.url:
        result.extracted_urls = [input_data.url]
        result.pipeline_steps.append("URL 직접 입력")

    elif input_data.input_type == "text" and input_data.text:
        result.extracted_text = input_data.text
        result.extracted_urls = extract_urls_from_text(input_data.text)
        result.pipeline_steps.append("텍스트 입력 처리 완료")

    result.extracted_urls = list(dict.fromkeys(result.extracted_urls))

    text_count = await db.scalar(select(func.count()).select_from(TextTrainingData))
    use_trained_text = (text_count or 0) >= settings.ml_switch_threshold
    if result.extracted_text:
        result.bert_result = classify_text(result.extracted_text, use_trained=use_trained_text)
        result.pipeline_steps.append(f"BERT 분류: {result.bert_result.smishing_type} ({result.bert_result.confidence:.0%})")
    else:
        result.bert_result = classify_text("")
        result.pipeline_steps.append("텍스트 없음 – BERT 분류 생략")

    if result.extracted_urls:
        result.safebrowsing_results = check_urls(result.extracted_urls)
        unsafe_count = sum(1 for r in result.safebrowsing_results if not r.is_safe)
        result.pipeline_steps.append(
            f"Safe Browsing: {len(result.extracted_urls)}개 URL 중 {unsafe_count}개 위험"
        )

        safe_urls = [r.url for r in result.safebrowsing_results if r.is_safe]
        url_count = await db.scalar(select(func.count()).select_from(UrlTrainingData))
        use_trained_url = (url_count or 0) >= settings.ml_switch_threshold
        if safe_urls:
            result.ml_url_results = score_urls(safe_urls, use_trained=use_trained_url)
            result.pipeline_steps.append(f"ML 2차 분석: {len(safe_urls)}개 URL 추가 분석")
        
        for sb in result.safebrowsing_results:
            if not sb.is_safe:
                result.ml_url_results.append(MLUrlResult(
                    url=sb.url, risk_score=90.0, risk_label="높음",
                    features={"safe_browsing_flagged": 1.0}
                ))
    else:
        result.pipeline_steps.append("URL 없음 – URL 분석 생략")

    result.group_risk = check_group_risk(
        result.bert_result.smishing_type if result.bert_result else None,
        result.extracted_urls,
    )
    if result.group_risk:
        result.pipeline_steps.append("집단 위험 신호 감지")

    max_url_score = max(
        (r.risk_score for r in result.ml_url_results), default=0
    )
    url_risk_label = (
        "높음" if max_url_score >= 70 else
        "중간" if max_url_score >= 40 else
        "낮음" if result.extracted_urls else "정보 부족"
    )

    url_domains = [r.url for r in result.ml_url_results[:3]] if result.ml_url_results else result.extracted_urls[:3]

    ner_entities = None
    if result.bert_result and result.bert_result.all_scores:
        ner_entities = [
            k for k, v in sorted(
                result.bert_result.all_scores.items(), key=lambda x: x[1], reverse=True
            ) if v > 0
        ][:5]

    result.rag_result, result.rag_engine, result.rag_error = await generate_guidance(
        db=db,
        smishing_type=result.bert_result.smishing_type if result.bert_result else "기타",
        url_risk_label=url_risk_label,
        url_domains=url_domains,
        ner_entities=ner_entities,
        group_risk=result.group_risk,
        masked_text=result.extracted_text[:100] if result.extracted_text else None,
    )
    result.pipeline_steps.append("RAG 가이드 생성 완료")

    return result
