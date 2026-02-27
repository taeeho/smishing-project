from pydantic import BaseModel, Field


class CoachInput(BaseModel):
    smishing_type: str | None = Field(default=None, description="BERT 분류 결과")
    url_risk_score: float | None = Field(default=None, description="URL 위험도 점수")
    url_domain: str | None = Field(default=None, description="추출된 도메인")
    ner_entities: list[str] | None = Field(default=None, description="NER 엔티티 목록")
    group_risk: bool | None = Field(default=None, description="집단 위험 여부")
    masked_text: str | None = Field(default=None, description="마스킹된 텍스트")
    input_type: str | None = Field(default=None, description="text/image")


class CoachSource(BaseModel):
    title: str
    source: str
    snippet: str


class CoachOutput(BaseModel):
    risk_summary: str
    evidence: list[str]
    recommended_actions: list[str]
    report_template: str
    guardian_summary: str
    sources: list[CoachSource]
