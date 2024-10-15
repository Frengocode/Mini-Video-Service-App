from sqlalchemy.orm import Mapped, mapped_column,  relationship
from sqlalchemy import String, Boolean, Integer, DateTime, Table, Column, ForeignKey
from datetime import datetime
from .database import Base
from .scheme import SUser

content_likes = Table(
    'video_likes', Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.id'), primary_key=True),
    Column('user_id', Integer, primary_key=True),
)

class VideoModel(Base):
    __tablename__ = 'videos'

    id: Mapped[int] = mapped_column(Integer, index = True, primary_key = True)
    video_title: Mapped[str] = mapped_column(String, nullable = False)
    date_pub: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow())
    video: Mapped[str] = mapped_column(String, nullable = False)
    video_category: Mapped[str] = mapped_column(String, nullable = False)
    is_exist: Mapped[bool] = mapped_column(Boolean, default = True)
    user_id: Mapped[int] = mapped_column(Integer)
    video_likes: Mapped[list[int]] = relationship('VideoModel', secondary=content_likes)
    # view_count: Mapped[int] = mapped_column(Integer, default=0)

