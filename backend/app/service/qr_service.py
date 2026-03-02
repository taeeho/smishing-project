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
