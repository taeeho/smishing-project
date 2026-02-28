"""
OCR 서비스 – 이미지에서 텍스트와 URL을 추출합니다.
실제 배포 시 pytesseract 또는 Cloud Vision API로 교체 가능합니다.
"""
from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass, field

# URL 정규식 – http(s)://... 또는 www.으로 시작하는 도메인
_URL_RE = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"
)


@dataclass
class OCRResult:
    """OCR 결과"""
    raw_text: str = ""
    extracted_urls: list[str] = field(default_factory=list)


def extract_urls_from_text(text: str) -> list[str]:
    """텍스트에서 URL을 추출합니다."""
    return _URL_RE.findall(text)


def ocr_from_base64(image_b64: str) -> OCRResult:
    """
    Base64 인코딩된 이미지에서 OCR을 수행합니다.
    현재는 시뮬레이션 모드 – 실제 pytesseract 설치 시 아래 주석 해제.
    """
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        return OCRResult(raw_text="[이미지 디코딩 실패]")

    # ── 실제 OCR (pytesseract 설치 필요) ──────────────────────
    # from PIL import Image
    # import pytesseract
    # img = Image.open(io.BytesIO(image_bytes))
    # raw = pytesseract.image_to_string(img, lang="kor+eng")
    # ──────────────────────────────────────────────────────────

    # ── 시뮬레이션 모드 ──────────────────────────────────────
    raw = _simulate_ocr(image_bytes)
    # ────────────────────────────────────────────────────────

    urls = extract_urls_from_text(raw)
    return OCRResult(raw_text=raw, extracted_urls=urls)


def ocr_from_bytes(image_bytes: bytes) -> OCRResult:
    """바이트 이미지로부터 OCR을 수행합니다."""
    # ── 실제 OCR ──
    # from PIL import Image
    # import pytesseract
    # img = Image.open(io.BytesIO(image_bytes))
    # raw = pytesseract.image_to_string(img, lang="kor+eng")

    raw = _simulate_ocr(image_bytes)
    urls = extract_urls_from_text(raw)
    return OCRResult(raw_text=raw, extracted_urls=urls)


# ─────────────────────────────────────────────────────────────
# 시뮬레이션 헬퍼
# ─────────────────────────────────────────────────────────────

def _simulate_ocr(image_bytes: bytes) -> str:
    """
    시뮬레이션: 이미지 크기에 따라 다른 샘플 텍스트를 반환합니다.
    실제 모델 교체 시 이 함수를 삭제하세요.
    """
    size = len(image_bytes)
    if size < 1000:
        return (
            "[Web발신] 택배 배송 실패. 주소 확인 바랍니다. "
            "https://fake-delivery.co.kr/track?id=12345"
        )
    elif size < 5000:
        return (
            "[국민건강보험] 건강검진 결과 확인 바랍니다. "
            "본인확인: https://nhis-check.xyz/verify "
            "미확인시 불이익이 있을 수 있습니다."
        )
    else:
        return (
            "긴급! 귀하의 계좌에서 비정상 출금이 감지되었습니다. "
            "즉시 확인하세요: https://bank-security-alert.com/check "
            "고객센터 1588-0000"
        )
