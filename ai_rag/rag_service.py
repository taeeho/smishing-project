from dataclasses import dataclass, field
import json
from typing import Any
import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.db.models.rag_document import RagDocument



_GUIDE_DB: dict[str, dict] = {
    "택배사칭": {
        "summary": "택배사를 사칭하여 배송 확인 URL 클릭을 유도하는 스미싱입니다.",
        "actions": [
            "문자 내 링크를 절대 클릭하지 마세요.",
            "택배사 공식 앱이나 홈페이지에서 직접 조회하세요.",
            "의심 문자를 캡처하여 스팸 신고하세요.",
            "118(한국인터넷진흥원) 또는 112에 신고하세요.",
        ],
        "faq": [
            {"q": "택배 URL을 이미 눌렀어요.", "a": "즉시 악성앱 검사를 실행하고, 비밀번호를 변경하세요. 112에 피해 접수하세요."},
            {"q": "개인정보를 입력했어요.", "a": "해당 서비스의 비밀번호를 즉시 변경하고, 금융감독원(1332)에 신고하세요."},
        ],
        "report_procedure": "1. 문자 캡처 → 2. 118 또는 112 전화 → 3. 내용 전달 → 4. 접수번호 보관",
        "similar_cases": "최근 CJ대한통운, 한진택배를 사칭한 SMS가 급증하고 있습니다.",
    },
    "기관사칭": {
        "summary": "정부기관이나 공공기관을 사칭하여 개인정보를 탈취하려는 스미싱입니다.",
        "actions": [
            "공공기관은 절대 문자로 개인정보를 요구하지 않습니다.",
            "해당 기관 공식 전화번호로 직접 확인하세요.",
            "링크를 클릭하지 말고 문자를 캡처하세요.",
            "경찰청(112) 또는 금감원(1332)에 신고하세요.",
        ],
        "faq": [
            {"q": "건강보험공단에서 온 문자 같은데요?", "a": "공단(1577-1000)에 직접 전화해서 확인하세요. 문자 링크는 사칭입니다."},
            {"q": "검찰/경찰이라며 전화가 왔어요.", "a": "수사기관은 전화로 계좌이체를 요구하지 않습니다. 끊고 112에 신고하세요."},
        ],
        "report_procedure": "1. 통화 녹음 또는 문자 캡처 → 2. 112 신고 → 3. 금감원 1332 추가 신고",
        "similar_cases": "국민건강보험, 국세청, 검찰청 사칭이 가장 빈번합니다.",
    },
    "금융사기": {
        "summary": "은행이나 금융기관을 사칭하여 계좌정보를 탈취하려는 스미싱입니다.",
        "actions": [
            "금융기관은 문자로 계좌번호나 비밀번호를 요구하지 않습니다.",
            "출금/이체 알림 시 해당 은행 앱에서 직접 확인하세요.",
            "의심스러운 앱 설치를 유도하면 절대 설치하지 마세요.",
            "금융감독원(1332) 또는 경찰(112)에 신고하세요.",
        ],
        "faq": [
            {"q": "계좌에서 돈이 빠져나갔어요.", "a": "즉시 은행 고객센터에 지급정지를 요청하고, 경찰에 신고하세요."},
            {"q": "대출 승인 문자를 받았어요.", "a": "사전 수수료를 요구하는 대출은 100% 사기입니다. 무시하세요."},
        ],
        "report_procedure": "1. 은행 콜센터 → 지급정지 → 2. 경찰 112 신고 → 3. 금감원 1332 피해구제 신청",
        "similar_cases": "카카오뱅크, 토스 등 핀테크 사칭과 저금리 대출 사기가 증가하고 있습니다.",
    },
    "지인사칭": {
        "summary": "가족이나 지인을 사칭하여 금전을 요구하는 메신저 피싱입니다.",
        "actions": [
            "반드시 직접 전화로 본인 확인하세요.",
            "급하다며 송금을 요구하면 의심하세요.",
            "문화상품권/기프티콘 구매 요청은 전형적인 사기 수법입니다.",
            "112에 신고하고, 해당 메신저 계정을 차단하세요.",
        ],
        "faq": [
            {"q": "이미 돈을 보냈어요.", "a": "즉시 은행에 지급정지를 요청하고, 112에 피해 접수하세요."},
            {"q": "지인 카톡이 해킹된 것 같아요.", "a": "해당 지인에게 다른 방법으로 연락하고, 카카오톡 고객센터에 신고하세요."},
        ],
        "report_procedure": "1. 은행 지급정지 → 2. 112 전화 신고 → 3. 메신저 계정 신고",
        "similar_cases": "카카오톡/라인 메신저를 통한 지인 사칭이 가장 많습니다.",
    },
    "피싱링크": {
        "summary": "인증이나 로그인을 가장하여 계정정보를 탈취하려는 피싱입니다.",
        "actions": [
            "문자/이메일 내 로그인 링크를 클릭하지 마세요.",
            "해당 서비스 앱이나 공식 웹사이트에서 직접 로그인하세요.",
            "이미 입력했다면 즉시 비밀번호를 변경하세요.",
            "118(KISA)에 피싱 신고하세요.",
        ],
        "faq": [
            {"q": "피싱 사이트에 로그인했어요.", "a": "즉시 비밀번호 변경 + 2단계 인증 설정하세요. 동일 비밀번호를 쓴 다른 서비스도 변경하세요."},
        ],
        "report_procedure": "1. 비밀번호 즉시 변경 → 2. 118 신고 → 3. 해당 서비스 고객센터 연락",
        "similar_cases": "네이버, 구글, 애플 계정을 노리는 피싱 페이지가 많습니다.",
    },
}

_DEFAULT_GUIDE = {
    "summary": "스미싱으로 의심되는 메시지입니다. 주의가 필요합니다.",
    "actions": [
        "문자 내 링크를 클릭하지 마세요.",
        "발신처를 직접 확인하세요.",
        "문자를 캡처해 두세요.",
        "112 또는 118에 신고하세요.",
    ],
    "faq": [],
    "report_procedure": "1. 문자 캡처 → 2. 112 또는 118 전화 → 3. 내용 전달",
    "similar_cases": "다양한 유형의 스미싱이 매일 발생하고 있습니다.",
}


@dataclass
class RAGSource:
    """RAG 참조 출처"""
    title: str
    source: str
    snippet: str


@dataclass
class RAGResult:
    """RAG 생성 결과"""
    risk_summary: str
    evidence: list[str]
    recommended_actions: list[str]
    report_template: str
    report_procedure: str
    guardian_summary: str
    coaching_steps: list[str]
    faq: list[dict]
    similar_cases: str
    sources: list[RAGSource] = field(default_factory=list)


def _assert_gemini_ready() -> None:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.",
        )


def _build_seed_docs() -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for key, guide in _GUIDE_DB.items():
        content = "\n".join([
            f"유형: {key}",
            f"요약: {guide['summary']}",
            f"행동: {'; '.join(guide['actions'])}",
            f"FAQ: " + " | ".join([f"Q:{f['q']} A:{f['a']}" for f in guide.get('faq', [])]),
            f"신고절차: {guide.get('report_procedure', '')}",
            f"유사사례: {guide.get('similar_cases', '')}",
        ])
        docs.append({
            "title": f"{key} 대응 가이드",
            "content": content,
            "source": "guide-database",
        })
    return docs


async def _embed_text(text: str, title: str | None = None, task_type: str | None = None) -> list[float]:
    _assert_gemini_ready()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_embed_model}:embedContent"
    payload: dict[str, Any] = {
        "content": {
            "parts": [{"text": text}],
        },
    }
    if task_type:
        payload["taskType"] = task_type
    if title and task_type == "RETRIEVAL_DOCUMENT":
        payload["title"] = title

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(url, params={"key": settings.gemini_api_key}, json=payload)

    if res.status_code != 200:
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Gemini 임베딩 생성 실패: {res.text}",
        )

    data = res.json()
    embedding = data.get("embedding", {}).get("values")
    if not embedding:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gemini 임베딩 응답이 비었습니다.")
    return embedding


async def _generate_with_gemini(prompt: str) -> str:
    _assert_gemini_ready()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(url, params={"key": settings.gemini_api_key}, json=payload)

    if res.status_code != 200:
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Gemini 생성 실패: {res.text}",
        )

    data = res.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gemini 응답 후보가 없습니다.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join([p.get("text", "") for p in parts]).strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gemini 응답 텍스트가 비었습니다.")
    return text


async def _ensure_seeded(db: AsyncSession) -> None:
    count = await db.scalar(select(func.count()).select_from(RagDocument))
    if count and count > 0:
        return

    docs = _build_seed_docs()
    for doc in docs:
        embedding = await _embed_text(doc["content"], title=doc["title"], task_type="RETRIEVAL_DOCUMENT")
        db.add(RagDocument(
            title=doc["title"],
            content=doc["content"],
            source=doc["source"],
            embedding=embedding,
        ))
    await db.commit()


async def _retrieve_docs(db: AsyncSession, query: str, top_k: int) -> list[RagDocument]:
    await _ensure_seeded(db)
    query_embedding = await _embed_text(query, task_type="RETRIEVAL_QUERY")

    stmt = (
        select(RagDocument)
        .order_by(RagDocument.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _build_prompt(
    smishing_type: str,
    url_risk_label: str,
    url_domains: list[str] | None,
    ner_entities: list[str] | None,
    group_risk: bool,
    masked_text: str | None,
    docs: list[RagDocument],
) -> str:
    context = "\n\n".join([f"[문서] {d.title}\n{d.content}" for d in docs])
    return (
        "너는 스미싱 대응 전문가다. 아래 컨텍스트를 참고해서 결과를 생성한다.\n"
        "형식은 한국어로, 간결하게 작성하고 허위 정보는 만들지 않는다.\n\n"
        f"컨텍스트:\n{context}\n\n"
        "분석 정보:\n"
        f"- 유형: {smishing_type}\n"
        f"- URL 위험도: {url_risk_label}\n"
        f"- URL: {', '.join(url_domains or [])}\n"
        f"- 키워드: {', '.join(ner_entities or [])}\n"
        f"- 집단 위험: {'예' if group_risk else '아니오'}\n"
        f"- 요약 텍스트: {masked_text or ''}\n\n"
        "아래 JSON 스키마에 맞춰 출력한다.\n"
        "{\n"
        "  \"risk_summary\": string,\n"
        "  \"evidence\": string[],\n"
        "  \"recommended_actions\": string[],\n"
        "  \"report_template\": string,\n"
        "  \"report_procedure\": string,\n"
        "  \"guardian_summary\": string,\n"
        "  \"coaching_steps\": string[],\n"
        "  \"faq\": [{\"q\": string, \"a\": string}],\n"
        "  \"similar_cases\": string\n"
        "}\n"
    )


async def generate_guidance(
    db: AsyncSession,
    smishing_type: str,
    url_risk_label: str = "정보 부족",
    url_domains: list[str] | None = None,
    ner_entities: list[str] | None = None,
    group_risk: bool = False,
    masked_text: str | None = None,
) -> tuple[RAGResult, str, str | None]:
    query = "\n".join([
        f"유형: {smishing_type}",
        f"위험도: {url_risk_label}",
        f"URL: {', '.join(url_domains or [])}",
        f"키워드: {', '.join(ner_entities or [])}",
    ])

    docs: list[RagDocument] = []
    rag_engine = "fallback"
    rag_error: str | None = None
    data: dict[str, Any] = {}
    try:
        docs = await _retrieve_docs(db, query=query, top_k=settings.rag_top_k)
        prompt = _build_prompt(
            smishing_type=smishing_type,
            url_risk_label=url_risk_label,
            url_domains=url_domains,
            ner_entities=ner_entities,
            group_risk=group_risk,
            masked_text=masked_text,
            docs=docs,
        )
        raw = await _generate_with_gemini(prompt)
        data = json.loads(raw) if raw.strip().startswith("{") else {"raw": raw}
        rag_engine = "gemini"
    except Exception as exc:
        data = {}
        rag_error = str(exc)

    guide = _GUIDE_DB.get(smishing_type, _DEFAULT_GUIDE)

    if url_risk_label == "안전":
        risk_summary = "안전한 것으로 확인되었습니다. 현재 위험도는 안전 수준입니다."
        evidence = [
            "화이트리스트 도메인 확인",
            "Safe Browsing 위험 신호 없음",
        ]
        recommended_actions = [
            "그래도 주소 철자를 한 번 더 확인하세요.",
            "공식 앱/즐겨찾기를 이용하면 더 안전합니다.",
        ]
    else:
        risk_summary = data.get("risk_summary") or f"{guide['summary']} 현재 위험도는 {url_risk_label} 수준입니다."
        evidence = data.get("evidence") or [f"분류 유형: {smishing_type}"]
        recommended_actions = data.get("recommended_actions") or guide["actions"]
    report_template = data.get("report_template") or (
        f"의심 문자 신고\n"
        f"유형: {smishing_type or '미분류'}\n"
        f"수신 일시: [날짜/시간]\n"
        f"문자 내용 요약: {masked_text or '[요약 입력]'}\n"
        f"의심 링크: {', '.join(url_domains[:2]) if url_domains else '[없음]'}\n"
        f"피해 여부: [미발생/발생]\n"
        f"요청 사항: 분석 및 차단 요청"
    )
    report_procedure = data.get("report_procedure") or guide.get("report_procedure", "112 또는 118에 신고하세요.")
    if url_risk_label == "안전":
        guardian_summary = "✅ 현재는 안전한 링크로 확인됩니다. 그래도 공식 채널 확인을 권장합니다."
    else:
        guardian_summary = data.get("guardian_summary") or (
            f"⚠️ 스미싱 의심 ({smishing_type or '미분류'}) | 위험도: {url_risk_label}. "
            f"링크 클릭·송금 중단 필요. 공식 채널로 확인 요망."
        )
    coaching_steps = data.get("coaching_steps") or [
        "1단계: 추가 피해 여부를 확인하세요 (계좌이체, 앱 설치 등).",
        "2단계: 금융 앱과 계좌를 점검하세요 (비정상 거래 확인).",
        "3단계: 보호자 또는 가족과 공유하세요.",
        "4단계: 필요 시 112(경찰) 또는 1332(금감원)에 신고하세요.",
        "5단계: 의심 번호를 차단하고 스팸 신고하세요.",
    ]
    faq = data.get("faq") or guide.get("faq", [])
    similar_cases = data.get("similar_cases") or guide.get("similar_cases", "")

    sources = [
        RAGSource(title=d.title, source=d.source, snippet=d.content[:120])
        for d in docs
    ]

    return RAGResult(
        risk_summary=risk_summary,
        evidence=evidence,
        recommended_actions=recommended_actions,
        report_template=report_template,
        report_procedure=report_procedure,
        guardian_summary=guardian_summary,
        coaching_steps=coaching_steps,
        faq=faq,
        similar_cases=similar_cases,
        sources=sources,
    ), rag_engine, rag_error
