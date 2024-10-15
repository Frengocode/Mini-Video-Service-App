from sqlalchemy.orm import Mapped, mapped_column
from  sqlalchemy import String, Integer, DateTime
from datetime import datetime
from src.services.comment_service.database import CommentBase



class CommentModel(CommentBase):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    video_id: Mapped[int] = mapped_column(Integer)
    date_pub: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    comment: Mapped[str] = mapped_column(String)
    

    