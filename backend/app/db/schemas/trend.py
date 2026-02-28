from __future__ import annotations

from pydantic import BaseModel


class TrendItem(BaseModel):
    label: str
    count: int
    similarity: float


class TrendResponse(BaseModel):
    age_group: str
    start_date: str
    end_date: str
    results: list[TrendItem]
