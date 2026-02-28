"""
Google Safe Browsing API 서비스
실제 배포 시 Google Safe Browsing API v4로 교체합니다.
현재는 도메인 패턴 기반 시뮬레이션으로 동작합니다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

# ── 의심 도메인 패턴 ─────────────────────────────────────────
_SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".buzz", ".click"}
_SUSPICIOUS_KEYWORDS = [
    "fake", "phish", "scam", "alert", "verify", "secure-login",
    "account-check", "bank-security", "nhis-check", "delivery-check",
    "suspicious", "urgent", "confirm",
]


@dataclass
class SafeBrowsingResult:
    """Safe Browsing 판별 결과"""
    url: str
    is_safe: bool
    threat_type: str | None = None  # MALWARE, SOCIAL_ENGINEERING, etc.
    detail: str = ""


def check_url(url: str) -> SafeBrowsingResult:
    """
    URL의 안전성을 판별합니다.

    실제 Google Safe Browsing API 교체 시:
        import httpx
        API_KEY = os.environ["GOOGLE_SAFE_BROWSING_API_KEY"]
        resp = httpx.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}",
            json={...}
        )
    """
    if not url:
        return SafeBrowsingResult(url=url, is_safe=True, detail="URL 없음")

    return _simulate_check(url)


def check_urls(urls: list[str]) -> list[SafeBrowsingResult]:
    """여러 URL을 한 번에 판별합니다."""
    return [check_url(u) for u in urls]


def _simulate_check(url: str) -> SafeBrowsingResult:
    """시뮬레이션: 도메인 패턴 기반 위험 판별"""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
    except Exception:
        return SafeBrowsingResult(url=url, is_safe=False, threat_type="PARSE_ERROR", detail="URL 파싱 실패")

    # TLD 검사
    for tld in _SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            return SafeBrowsingResult(
                url=url,
                is_safe=False,
                threat_type="SOCIAL_ENGINEERING",
                detail=f"의심 TLD 감지: {tld}",
            )

    # 키워드 검사
    full = domain + path
    for kw in _SUSPICIOUS_KEYWORDS:
        if kw in full:
            return SafeBrowsingResult(
                url=url,
                is_safe=False,
                threat_type="SOCIAL_ENGINEERING",
                detail=f"의심 키워드 감지: {kw}",
            )

    # IP 기반 URL 검사
    if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        return SafeBrowsingResult(
            url=url,
            is_safe=False,
            threat_type="MALWARE",
            detail="IP 주소 기반 URL 감지",
        )

    return SafeBrowsingResult(url=url, is_safe=True, detail="안전한 것으로 판별됨")
