from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from src.services.view_service.database import ViewBase
from datetime import datetime


class ViewModel(ViewBase):
    __tablename__ = "views"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    video_id: Mapped[int] = mapped_column(Integer)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())