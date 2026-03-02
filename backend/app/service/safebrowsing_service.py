import re
from dataclasses import dataclass
from urllib.parse import urlparse
import httpx
from app.core.settings import settings

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
    """URL의 안전성을 판별합니다."""
    if not url:
        return SafeBrowsingResult(url=url, is_safe=True, detail="URL 없음")

    return check_urls([url])[0]


def check_urls(urls: list[str]) -> list[SafeBrowsingResult]:
    """여러 URL을 한 번에 판별합니다."""
    api_key = settings.google_safe_browsing_api_key
    if not api_key:
        return [
            SafeBrowsingResult(
                url=u,
                is_safe=True,
                detail="Safe Browsing API 키가 설정되지 않아 검사 생략",
            )
            for u in urls
        ]

    threats = []
    for u in urls:
        if u:
            threats.append({"url": u})

    payload = {
        "client": {"clientId": "qcheck", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": threats,
        },
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}",
                json=payload,
            )
        if resp.status_code != 200:
            return [
                SafeBrowsingResult(
                    url=u,
                    is_safe=True,
                    detail=f"Safe Browsing API 오류: {resp.status_code}",
                )
                for u in urls
            ]
        data = resp.json() or {}
    except Exception:
        return [
            SafeBrowsingResult(url=u, is_safe=True, detail="Safe Browsing API 호출 실패")
            for u in urls
        ]

    matches = data.get("matches", []) or []
    matched_map: dict[str, dict] = {}
    for m in matches:
        entry = m.get("threat", {})
        m_url = entry.get("url")
        if m_url:
            matched_map[m_url] = m

    results: list[SafeBrowsingResult] = []
    for u in urls:
        m = matched_map.get(u)
        if m:
            results.append(
                SafeBrowsingResult(
                    url=u,
                    is_safe=False,
                    threat_type=m.get("threatType"),
                    detail="Safe Browsing 매칭",
                )
            )
        else:
            results.append(SafeBrowsingResult(url=u, is_safe=True, detail="Safe Browsing 통과"))

    return results


def _simulate_check(url: str) -> SafeBrowsingResult:
    """시뮬레이션: 도메인 패턴 기반 위험 판별 (보조용)"""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
    except Exception:
        return SafeBrowsingResult(url=url, is_safe=False, threat_type="PARSE_ERROR", detail="URL 파싱 실패")

    for tld in _SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            return SafeBrowsingResult(
                url=url,
                is_safe=False,
                threat_type="SOCIAL_ENGINEERING",
                detail=f"의심 TLD 감지: {tld}",
            )

    full = domain + path
    for kw in _SUSPICIOUS_KEYWORDS:
        if kw in full:
            return SafeBrowsingResult(
                url=url,
                is_safe=False,
                threat_type="SOCIAL_ENGINEERING",
                detail=f"의심 키워드 감지: {kw}",
            )

    if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        return SafeBrowsingResult(
            url=url,
            is_safe=False,
            threat_type="MALWARE",
            detail="IP 주소 기반 URL 감지",
        )

    return SafeBrowsingResult(url=url, is_safe=True, detail="안전한 것으로 판별됨")
