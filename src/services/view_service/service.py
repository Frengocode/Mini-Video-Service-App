from sqlalchemy.ext.asyncio import AsyncSession
from src.services.view_service.models import ViewModel
from src.kafka_server.main import get_kafka_producer
from aiokafka import AIOKafkaProducer
from src.services.view_service.scheme import ViewResponse, VideoReponse, SUser
import httpx
import logging
from sqlalchemy import select
from fastapi import HTTPException
import asyncio
from src.uitils.auth import get_current_user
from fastapi import Depends


log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class ViewService:

    def __init__(self, session: AsyncSession, kafka_client: AIOKafkaProducer):
        self.session = session
        self.kafka_client = kafka_client

    async def send_request_to_kafka(self, video_id: int):

        
        topic = "fetch-video-data"
        message = {
            "video_id": video_id,
        }

        try:

            await self.kafka_client.send_and_wait(
                topic, value=str(message).encode("utf-8")
            )
            log.info(f"Sent request to Kafka for video_id {video_id}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8000/video-service/get-video/{video_id}"
                )

            if response.status_code == 200:
                return response.json()
            
            else:
                log.warning(f"Failed to fetch video: {response.status_code}")
                return None

        except Exception as e:
            log.error(f"Error sending message to Kafka: {e}")
            return None
        


    async def create_view_for_video(self, current_user: SUser, video_id: int):

        view_query = await self.session.execute(
            select(ViewModel).filter_by(video_id=video_id, user_id=current_user.id)
        )

        view = view_query.scalars().first()

        tasks = [self.send_request_to_kafka(video_id)]

        responses = await asyncio.gather(*tasks)

        if not responses or not responses[0]:
            raise HTTPException(detail="Not Found", status_code=404)

        video_data = responses[0]

        if view:
            raise HTTPException(detail="Already Added", status_code=402)

        view_ = ViewModel(user_id=current_user.id, video_id=video_data.get("id"))

        self.session.add(view_)
        await self.session.commit()

        return {"detail": "View Created Successfully"}

    async def get_user_viewed_video(self, current_user: SUser):

        viewed_video_query = await self.session.execute(
            select(ViewModel)
            .order_by(ViewModel.viewed_at.desc())
            .filter(ViewModel.user_id == current_user.id)
        )

        viewed_video = viewed_video_query.scalars().all()

        tasks = [
            self.send_request_to_kafka(view_video.video_id)
            for view_video in viewed_video
        ]

        video_responses = await asyncio.gather(*tasks)

        response = []

        for i, viewed in enumerate(viewed_video):
            video_data = video_responses[i]

            if video_data:
                response.append(
                    ViewResponse(
                        id=viewed.id,
                        video=(
                            VideoReponse(
                                id=video_data.get("id"),
                                video_title=video_data.get("video_title"),
                                video=video_data.get("video"),
                                category=video_data.get("category"),
                                date_pub=video_data.get("date_pub"),
                                user=(
                                    SUser(
                                        id=video_data.get("user").get("id"),
                                        username=video_data.get("user").get("username"),
                                    )
                                    if video_data.get("user")
                                    else None
                                ),
                            )
                            if video_data
                            else None
                        ),
                        user_id=viewed.user_id,
                        viewed_at=viewed.viewed_at,
                    )
                )

        return response

    async def delete_view(self, current_user: SUser, view_id: int):

        view_query = await self.session.execute(
            select(ViewModel).filter_by(user_id=current_user.id, id=view_id)
        )

        view = view_query.scalars().first()
        if not view:
            log.warning(f"View Not Found with id {view_id}")
            raise HTTPException(detail="Not Found", status_code=404)

        await self.session.delete(view)
        log.info("View Deleted")
        await self.session.commit()

        return f"View with id {view_id} deleted"
