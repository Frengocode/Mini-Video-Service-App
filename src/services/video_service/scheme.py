from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class VideoCategory(Enum):
    FOR_KIDS = 'For Kids'
    FOR_ALL = 'For All'


class SUser(BaseModel):
    id: int = None
    username: str = None


class VideoReponse(BaseModel):
    id: int
    video_title: str
    video: str
    date_pub: datetime
    category: str
    user: Optional[SUser] = None