"""
ML URL 위험도 스코어링 서비스 (2차 판별)
LogisticRegression / RandomForest 시뮬레이션
실제 배포 시 학습된 sklearn 모델(joblib)로 교체합니다.
"""
from __future__ import annotations

import re
import math
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class MLUrlResult:
    """ML URL 위험도 결과"""
    url: str
    risk_score: float          # 0.0 ~ 100.0
    risk_label: str            # 높음 / 중간 / 낮음
    features: dict[str, float] # 추출된 특성값


def score_url(url: str) -> MLUrlResult:
    """
    URL에서 특성을 추출하고 위험도(%)를 산출합니다.

    실제 모델 교체 시:
        import joblib
        model = joblib.load("models/url_risk_model.pkl")
        features = extract_features(url)
        score = model.predict_proba([features])[0][1] * 100
    """
    features = _extract_features(url)
    risk_score = _simulate_score(features)
    risk_label = _score_to_label(risk_score)

    return MLUrlResult(
        url=url,
        risk_score=round(risk_score, 1),
        risk_label=risk_label,
        features=features,
    )


def score_urls(urls: list[str]) -> list[MLUrlResult]:
    """여러 URL의 위험도를 산출합니다."""
    return [score_url(u) for u in urls]


# ─────────────────────────────────────────────────────────────
# Feature Extraction
# ─────────────────────────────────────────────────────────────

def _extract_features(url: str) -> dict[str, float]:
    """URL에서 ML 특성을 추출합니다."""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
    except Exception:
        return {"url_length": len(url), "error": 1.0}

    return {
        "url_length": float(len(url)),
        "domain_length": float(len(domain)),
        "path_length": float(len(path)),
        "query_length": float(len(query)),
        "dot_count": float(domain.count(".")),
        "hyphen_count": float(domain.count("-")),
        "digit_ratio": _digit_ratio(domain),
        "has_ip": float(bool(re.match(r"\d+\.\d+\.\d+\.\d+", domain))),
        "has_https": float(parsed.scheme == "https"),
        "special_char_count": float(len(re.findall(r"[^a-zA-Z0-9./\-_?=&]", url))),
        "subdomain_count": float(max(domain.count(".") - 1, 0)),
        "path_depth": float(path.count("/")),
    }


def _digit_ratio(s: str) -> float:
    """문자열에서 숫자 비율"""
    if not s:
        return 0.0
    return sum(c.isdigit() for c in s) / len(s)


# ─────────────────────────────────────────────────────────────
# Scoring (시뮬레이션)
# ─────────────────────────────────────────────────────────────

def _simulate_score(features: dict[str, float]) -> float:
    """
    특성값 기반 가중합으로 위험도를 시뮬레이션합니다.
    실제 모델 교체 시 이 함수를 삭제합니다.
    """
    weights = {
        "url_length": 0.15,
        "domain_length": 0.05,
        "hyphen_count": 8.0,
        "digit_ratio": 30.0,
        "has_ip": 40.0,
        "special_char_count": 5.0,
        "subdomain_count": 10.0,
        "path_depth": 3.0,
        "has_https": -5.0,  # HTTPS는 약간 감점
    }

    raw = sum(features.get(k, 0) * w for k, w in weights.items())

    # sigmoid로 0~100 범위로 변환
    score = 100 / (1 + math.exp(-0.05 * (raw - 20)))
    return max(0.0, min(100.0, score))


def _score_to_label(score: float) -> str:
    if score >= 70:
        return "높음"
    if score >= 40:
        return "중간"
    return "낮음"
