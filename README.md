# Qcheck 스미싱 예방 코치 (개인 프로젝트)

문자, URL, 이미지에서 스미싱 위험을 빠르게 판단하고 사용자에게 이해하기 쉬운 대응 가이드를 제공하는 개인 프로젝트입니다. 기획부터 설계, 구현, 배포 구성까지 전부 단독으로 진행했습니다.

## 주제 선정 이유

스미싱은 일상적으로 가장 많이 접하는 디지털 범죄 유형 중 하나인데, 사용자는 보통 위험 판단 기준을 알기 어렵습니다. 지금 안전한가/위험한가를 즉시 알려주고, 다음 행동을 안내하는 도구가 필요하다고 판단해 이 주제를 선택했습니다.

## 핵심 목표

- 입력 방식을 다양화해 실제 사용 흐름에 가까운 분석 경험 제공
- 위험도 판단 결과를 요약과 행동 가이드로 연결
- 분석 이력과 트렌드를 통해 사용자 관찰 가능
- 모델 전환과 확장성을 고려한 구조 설계

## 주요 기능

- 이미지/텍스트/URL/QR 분석
- 위험도 요약, 근거 제시, 대응 가이드 제공
- 분석 기록 저장 및 조회
- 트렌드 집계(나이대별, 최근 1년 Top 10)
- 카카오 로그인 기반 사용자 관리

## 폴더 구조

```text
Qcheck/
  frontend/
    Dockerfile
    src/
    public/
    index.html
    package.json
    vite.config.js
  backend/
    Dockerfile
    app/
    alembic/
    requirements.txt
    main.py
    .env
  ai_ocr/
    ocr_service.py
  ai_rag/
    rag_service.py
  ai_bert/
    bert_service.py
  ai_group_risk/
    group_risk.py
  docker-compose.yml
  .env
  README.md
```

## 아키텍처 요약

- `frontend`: 사용자 입력, 결과 시각화
- `backend`: 인증, 분석 파이프라인, 기록 저장, 트렌드 집계
- `ai_ocr`: 이미지 → 텍스트 추출
- `ai_rag`: 위험 요약/가이드 생성
- `ai_bert`: 유형 분류(현재 LLM 기반, 향후 실모델 전환 가능)
- `ai_group_risk`: 집단 위험 판단

## 실행 방법 (Docker)

```bash
podman compose up --build
```

## 분석 흐름

1. 로그인(카카오)
2. 입력(이미지/텍스트/URL/QR)
3. 파이프라인 실행 (OCR → 분류 → URL 위험도 → RAG 가이드)
4. 결과 화면 표시
5. 기록 저장 및 트렌드 집계

## 참고

- OCR은 Tesseract 기반으로 동작합니다.
- RAG는 Gemini + pgvector로 구성되며, 실패 시 기본 가이드로 fallback 됩니다.
- 모델 전환을 고려해 학습 데이터가 일정량 이상 축적되면 실모델로 확장 가능한 구조입니다.
