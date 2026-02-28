"""
QR 디코더 서비스 – QR 코드 이미지에서 URL을 추출합니다.
실제 배포 시 pyzbar 라이브러리로 교체 가능합니다.
"""
from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field


@dataclass
class QRResult:
    """QR 디코딩 결과"""
    decoded_urls: list[str] = field(default_factory=list)
    raw_data: list[str] = field(default_factory=list)
    success: bool = False


def decode_qr_from_base64(image_b64: str) -> QRResult:
    """Base64 인코딩된 QR 이미지를 디코딩합니다."""
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        return QRResult(success=False)

    return decode_qr_from_bytes(image_bytes)


def decode_qr_from_bytes(image_bytes: bytes) -> QRResult:
    """바이트 QR 이미지를 디코딩합니다."""

    # ── 실제 QR 디코딩 (pyzbar + PIL 설치 필요) ─────────────
    # from PIL import Image
    # from pyzbar.pyzbar import decode
    # img = Image.open(io.BytesIO(image_bytes))
    # results = decode(img)
    # raw_data = [r.data.decode("utf-8") for r in results]
    # urls = [d for d in raw_data if d.startswith("http")]
    # return QRResult(decoded_urls=urls, raw_data=raw_data, success=bool(results))
    # ──────────────────────────────────────────────────────────

    # ── 시뮬레이션 모드 ──────────────────────────────────────
    return _simulate_qr(image_bytes)


def _simulate_qr(image_bytes: bytes) -> QRResult:
    """
    시뮬레이션: QR 코드가 특정 URL을 포함하는 것으로 가정합니다.
    """
    simulated_url = "https://suspicious-qr-link.co.kr/event?code=QR9876"
    return QRResult(
        decoded_urls=[simulated_url],
        raw_data=[simulated_url],
        success=True,
    )
