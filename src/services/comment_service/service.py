from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.services.comment_service.models import CommentModel
from src.services.view_service.scheme import SUser
from aiokafka import AIOKafkaProducer
import asyncio
import httpx
import logging
from src.requests.request import GET_USER_REQUEST, GET_VIDEO_REQUEST
from src.services.comment_service.scheme import CommentResponse
from fastapi import HTTPException


log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)

class CommentService:
    def __init__(self, session: AsyncSession, kafka_client: AIOKafkaProducer, auth_response: SUser, comment_response: CommentResponse):
        
        self.kafka_client = kafka_client
        self.session = session
        self.auth_response = auth_response
        self.comment_response = comment_response


    async def fetch_user_data(self, user_id: int):
        topic = 'fetch-user-data'
        message = {
            "user_id": user_id,
            }

        try:
            await self.kafka_client.send_and_wait(topic, value=str(message).encode('utf-8'))
            log.info(f"Sent request to Kafka for user_id {user_id}")

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{GET_USER_REQUEST}/{user_id}")

            if response.status_code == 200:
                return response.json()
            else:
                log.warning(f"Failed to fetch user: {response.status_code}")
                return None
            
        except Exception as e:
            log.error(f"Error sending message to Kafka: {e}")
            return None
        

        
    async def fetch_video_data(self, video_id: int):
        topic = 'fetch-video-data'
        message = {
            "video_id": video_id,
            }

        try:
            await self.kafka_client.send_and_wait(topic, value=str(message).encode('utf-8'))
            log.info(f"Sent request to Kafka for video_id {video_id}")

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{GET_VIDEO_REQUEST}/{video_id}")

            if response.status_code == 200:
                return response.json()
            else:
                log.warning(f"Failed to fetch video: {response.status_code}")
                return None
            
        except Exception as e:
            log.error(f"Error sending message to Kafka: {e}")
            return None


    
    async def create_comment(self, current_user: SUser, comment: str, video_id: int):
        

        tasks = [self.fetch_video_data(video_id)]

        responses = await asyncio.gather(*tasks)

        if not responses or not responses[0]:
            raise HTTPException(detail="Video Not Found", status_code=404)

        video_data = responses[0]

        if not video_data:
            log.warning("Cannot Getting User Data")

        new_comment = CommentModel(

            comment = comment,
            video_id = video_data.get("id"),
            user_id = current_user.id

        )

        self.session.add(new_comment)
        await self.session.commit()
        log.info("Yee Comment Created Succsesfully")

        return {"detail": f"Comment Created Succsesfully on {video_id}"}
    


    async def get_all_comments(self, current_user: SUser, video_id: int):

        comments_query = await self.session.execute(
            select(CommentModel)
            .filter(CommentModel.video_id == video_id)
            .order_by(CommentModel.date_pub.desc())
        )
        
        comments = comments_query.scalars().all()


        request_to_kafka = [
            self.fetch_user_data(comment.user_id)
            for comment in comments
        ]


        responses = await asyncio.gather(*request_to_kafka)


        user_data = responses[0]
        if not user_data:
            log.warn("Cannot Getting User data")

        comment_response = [
            self.comment_response(
                id=comment.id,
                user=self.auth_response(
                    id=user_data.get("id"),  
                    username=user_data.get("username")
                ),
                comment=comment.comment,
                date_pub=comment.date_pub,
                video_id = comment.video_id,
            )
            for comment in comments
        ]


        return comment_response



    async def delete_comment(self, current_user: SUser, comment_id: int):
        
        comment_query = await self.session.execute(

            select(CommentModel)
            .filter_by(id = comment_id, user_id = current_user.id)
        )

        comment = comment_query.scalars().first()
        if not comment:
            raise HTTPException(
                detail = "Not Found",
                status_code=404
            )
        
        await self.session.delete(comment)
        await self.session.commit()
        
        return {"detail": 'Deleted Succsesfully'}