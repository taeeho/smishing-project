import base64
import io
import re
from dataclasses import dataclass, field
from PIL import Image
import pytesseract

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


def _run_tesseract(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(img, lang="kor+eng")


def ocr_from_base64(image_b64: str) -> OCRResult:
    """
    Base64 인코딩된 이미지에서 OCR을 수행합니다.
    """
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        return OCRResult(raw_text="[이미지 디코딩 실패]")

    raw = _run_tesseract(image_bytes)
    urls = extract_urls_from_text(raw)
    return OCRResult(raw_text=raw, extracted_urls=urls)


def ocr_from_bytes(image_bytes: bytes) -> OCRResult:
    """바이트 이미지로부터 OCR을 수행합니다."""
    raw = _run_tesseract(image_bytes)
    urls = extract_urls_from_text(raw)
    return OCRResult(raw_text=raw, extracted_urls=urls)
