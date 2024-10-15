from pydantic import BaseModel
from typing import Optional
from src.services.video_service.scheme import SUser
from datetime import datetime

class CommentResponse(BaseModel):
    id: int
    user: Optional[SUser] = None
    video_id: int
    comment: str
    date_pub: datetime