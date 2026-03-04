from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.database import Base


class UrlTrainingData(Base):
    __tablename__ = "url_training_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    features_json: Mapped[str] = mapped_column(Text, nullable=False)
    risk_label: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone("Asia/Seoul", func.now()), nullable=False)
