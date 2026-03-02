from dataclasses import dataclass
import json
import httpx
from app.core.settings import settings

_pipeline = None


def _load_transformer_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if not settings.bert_model_path:
        return None
    try:
        from transformers import pipeline
        _pipeline = pipeline("text-classification", model=settings.bert_model_path)
        return _pipeline
    except Exception:
        return None


LABELS = [
    "택배사칭",
    "기관사칭",
    "금융사기",
    "지인사칭",
    "피싱링크",
    "기타",
    "판별불가",
]


@dataclass
class BERTResult:
    """분류 결과"""
    smishing_type: str
    confidence: float
    all_scores: dict[str, float]


def _assert_gemini_ready() -> None:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")


def _build_prompt(text: str) -> str:
    return (
        "너는 스미싱 유형 분류기다. 아래 텍스트를 가장 적절한 한 가지 유형으로 분류해라.\n"
        "가능한 유형: 택배사칭, 기관사칭, 금융사기, 지인사칭, 피싱링크, 기타, 판별불가\n"
        "반드시 JSON으로만 답하라.\n"
        "{\n"
        '  "label": string,\n'
        '  "confidence": number\n'
        "}\n\n"
        f"텍스트: {text}"
    )


def _call_gemini(prompt: str) -> str:
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
    with httpx.Client(timeout=20) as client:
        res = client.post(url, params={"key": settings.gemini_api_key}, json=payload)
    if res.status_code != 200:
        raise RuntimeError(f"Gemini 분류 실패: {res.text}")
    data = res.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini 분류 응답이 비었습니다.")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join([p.get("text", "") for p in parts]).strip()
    if not text:
        raise RuntimeError("Gemini 분류 응답 텍스트가 비었습니다.")
    return text


def classify_text(text: str, use_trained: bool = False) -> BERTResult:
    """LLM으로 스미싱 유형을 분류합니다. 학습 모델이 있으면 우선 사용합니다."""
    if not text or not text.strip():
        return BERTResult(
            smishing_type="판별불가",
            confidence=0.0,
            all_scores={"판별불가": 1.0},
        )

    if use_trained:
        clf = _load_transformer_pipeline()
        if clf:
            try:
                out = clf(text)[0]
                label = out.get("label", "기타")
                score = float(out.get("score", 0.5))
                if label not in LABELS:
                    label = "기타"
                return BERTResult(
                    smishing_type=label,
                    confidence=round(max(min(score, 1.0), 0.0), 3),
                    all_scores={label: round(max(min(score, 1.0), 0.0), 3)},
                )
            except Exception:
                pass

    try:
        prompt = _build_prompt(text)
        raw = _call_gemini(prompt)
        data = json.loads(raw) if raw.strip().startswith("{") else {}
        label = data.get("label")
        confidence = float(data.get("confidence", 0.5))
        if label not in LABELS:
            label = "기타"
        return BERTResult(
            smishing_type=label,
            confidence=round(max(min(confidence, 1.0), 0.0), 3),
            all_scores={label: round(max(min(confidence, 1.0), 0.0), 3)},
        )
    except Exception:
        return BERTResult(
            smishing_type="판별불가",
            confidence=0.0,
            all_scores={"판별불가": 1.0},
        )
