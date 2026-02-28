"""
BERT 스미싱 유형 분류 서비스
실제 배포 시 학습된 BERT 모델(transformers)로 교체 가능합니다.
현재는 키워드 기반 규칙 시뮬레이션으로 동작합니다.
"""
from __future__ import annotations

from dataclasses import dataclass

# ── 스미싱 유형 정의 ─────────────────────────────────────────
SMISHING_TYPES = {
    "택배사칭": ["택배", "배송", "운송장", "물류", "반품", "수령", "배달"],
    "기관사칭": ["국민건강보험", "국세청", "검찰", "경찰", "법원", "정부", "공공기관", "질병관리청", "금감원"],
    "금융사기": ["계좌", "출금", "이체", "대출", "카드", "결제", "은행", "금융", "투자", "수익"],
    "지인사칭": ["엄마", "아빠", "아들", "딸", "선생님", "친구", "급해", "부탁", "돈 좀"],
    "피싱링크": ["확인하세요", "클릭", "로그인", "인증", "본인확인", "비밀번호"],
}


@dataclass
class BERTResult:
    """BERT 분류 결과"""
    smishing_type: str
    confidence: float
    all_scores: dict[str, float]


def classify_text(text: str) -> BERTResult:
    """
    텍스트를 스미싱 유형으로 분류합니다.

    실제 BERT 모델 교체 시:
        from transformers import pipeline
        classifier = pipeline("text-classification", model="path/to/bert-smishing")
        result = classifier(text)
    """
    if not text or not text.strip():
        return BERTResult(
            smishing_type="판별불가",
            confidence=0.0,
            all_scores={"판별불가": 1.0},
        )

    text_lower = text.lower()
    scores: dict[str, float] = {}

    for stype, keywords in SMISHING_TYPES.items():
        matched = sum(1 for kw in keywords if kw in text_lower)
        # 매칭 키워드 수를 전체 키워드 수로 나누어 점수 계산
        scores[stype] = min(matched / max(len(keywords) * 0.3, 1), 1.0)

    # 점수가 모두 0이면 판별불가
    if max(scores.values()) == 0:
        return BERTResult(
            smishing_type="기타",
            confidence=0.3,
            all_scores={**scores, "기타": 0.3},
        )

    best_type = max(scores, key=scores.get)  # type: ignore
    best_score = scores[best_type]

    # confidence 보정 (시뮬레이션이므로 0.6~0.95 범위)
    confidence = min(0.6 + best_score * 0.35, 0.95)

    return BERTResult(
        smishing_type=best_type,
        confidence=round(confidence, 3),
        all_scores={k: round(v, 3) for k, v in scores.items()},
    )
