from pydantic import BaseModel
from typing import Optional
from src.services.video_service.scheme import VideoReponse, SUser
from datetime import datetime



class ViewResponse(BaseModel):
    id: int
    video: VideoReponse = None
    user_id: int
    viewed_at: datetime