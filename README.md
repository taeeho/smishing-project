# 스미싱 예방 코치 (개인 프로젝트)

본 프로젝트는 개인이 단독으로 설계·개발한 스미싱 예방/분석 서비스입니다. 모든 기능과 구현은 제 개인 작업 결과이며, 외부 기여 없이 진행되었습니다.

---

## 프로젝트 개요

- 스미싱 문자/URL/이미지 분석
- 위험도 요약, 근거 제시, 대응 가이드 제공
- 분석 기록 저장 및 조회
- 트렌드 집계(나이대별, 최근 1년 Top 10)
- 카카오 로그인 기반 사용자 관리

---

## 폴더 구조

```
/Users/hataeho/Documents/new
├── backend/          # FastAPI 백엔드
├── frontend/         # React + Vite 프론트엔드
├── ai_ocr/           # OCR 모듈 (Tesseract)
├── ai_bert/          # 스미싱 유형 분류 (규칙 기반 시뮬레이션)
├── ai_group_risk/    # 집단 위험 판단 모듈
├── ai_rag/           # RAG 가이드 (Gemini + pgvector)
└── docs/             # 문서
```

---

## 실행 방법 (Docker)

```
podman compose up --build
```

---

## 주요 흐름

1. 로그인(카카오)
2. 입력(이미지/텍스트/URL)
3. 분석 파이프라인 (OCR → 분류 → URL 위험도 → RAG 가이드)
4. 결과 화면 표시
5. 기록 저장 및 트렌드 집계

---

## 참고

- OCR은 Tesseract 기반으로 동작합니다.
- BERT 분류는 현재 규칙 기반 시뮬레이션입니다.
- RAG는 Gemini + pgvector로 구성되어 있으며, Gemini 실패 시 기본 가이드로 fallback 됩니다.
