from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Form, UploadFile, File, Depends
from sqlalchemy import select
from src.services.video_service.models import VideoModel, content_likes
from src.uitils.auth import get_current_user
from .scheme import VideoCategory, SUser, VideoReponse
import uuid
import os
import httpx
from typing import List
import asyncio
import logging
from aiokafka import AIOKafkaProducer
from src.requests.request import GET_USER_REQUEST
import aiofiles



log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


MEDIA_ROOT = "media/video/"


class VideoModelService:
    def __init__(self, session: AsyncSession, kafka_producer: AIOKafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create_video(
        self,
        category: VideoCategory,
        current_user: SUser = Depends(get_current_user),
        title: str = Form(...),
        video: UploadFile = File(...),
    ):

        video.filename = f"{uuid.uuid4()}.mp4"
        file_path = os.path.join(MEDIA_ROOT, video.filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await video.read(1024): 
                await out_file.write(content)
        log.info(f"Video {video.filename} saved at {file_path}")


        video_ = VideoModel(
            video_title=title,
            user_id=current_user.id,
            video=video.filename,
            video_category=category,
        )

        
        self.session.add(video_)
        await self.session.commit()
        

    async def get_all_video(self, current_user: SUser):

        video_query = await self.session.execute(
            select(VideoModel)
            .order_by(VideoModel.date_pub.desc())
            .filter(VideoModel.is_exist != False)
        )

        videos = video_query.scalars().all()

        tasks = [
            self.send_request_to_kafka(video.user_id)
            for video in videos
        ]

        responses = await asyncio.gather(*tasks)

        video_responses = []
        for video, response in zip(videos, responses):
            user_data = response
            if not user_data:
                log.warn("Error Of getting user data")

            video_responses.append(
                VideoReponse(
                    id=video.id,
                    user=SUser(
                        id=user_data.get("id"), 
                        username = user_data.get("username")
                    )if user_data else None,

                    date_pub=video.date_pub,
                    video=video.video,
                    video_title=video.video_title,
                    category=video.video_category,
                )
            )

        return video_responses

    async def get_video_with_id(
        self,  video_id: int
    ) -> VideoReponse:

        video_query = await self.session.execute(
            select(VideoModel).filter_by(id = video_id, is_exist = True)

        )

        video = video_query.scalars().first()
        if not video:
            log.error("Video Not Found")
            raise HTTPException(detail="Not Found", status_code=404)


        tasks = [
            self.send_request_to_kafka(video.user_id)
        ]

        responses = await asyncio.gather(*tasks)

        user_data = responses[0]

        if not user_data:
            log.warning("Cannot Getting User Data")

        response = VideoReponse(
            id=video.id,
            video=video.video,
            video_title=video.video_title,
            category=video.video_category,
            user=SUser(id=user_data.get("id"), username=user_data.get("username"))if user_data else None,
            date_pub=video.date_pub,
        )

        return response

    async def get_video_by_category(
        self, current_user: SUser, category: VideoCategory
    ) -> List[VideoReponse]:

        video_query = await self.session.execute(
            select(VideoModel)
            .filter(VideoModel.video_category == category)
            .filter(VideoModel.is_exist != False)
            .order_by(VideoModel.date_pub.desc())
        )

        videos = video_query.scalars().all()
        if not videos:
            raise []


        tasks = [
            self.send_request_to_kafka(video.user_id)
            for video in videos
        ]

        responses = await asyncio.gather(*tasks)

        user_data = responses[0]
        if not user_data:
            log.warning("Cant getting User data")

        response = [
            VideoReponse(
                id=video.id,
                video=video.video,
                video_title=video.video_title,
                user=SUser(
                    id=user_data.get("id"), username=user_data.get("username")
                ),
                date_pub=video.date_pub,
                category=video.video_category,
            )
            for video in videos
        ]

        return response

    async def get_all_user_videos(
        self, current_user: SUser, user_id: int, **kwargs
    ) -> List[VideoReponse] | None:

        video_query = await self.session.execute(
            select(VideoModel)
            .filter(VideoModel.is_exist != False)
            .order_by(VideoModel.date_pub.desc())
            .filter(VideoModel.user_id == user_id)
        )

        videos = video_query.scalars().all()
        if not videos:
            return []


        tasks = [
            self.send_request_to_kafka(video.user_id)
            for video in videos
        ]

        responses = await asyncio.gather(*tasks)

        user_data = responses[0]
        if not user_data:
            log.warning("Cant getting User data")

        response = [
            VideoReponse(
                id=video.id,
                video=video.video,
                video_title=video.video_title,
                date_pub=video.date_pub,
                user=SUser(
                    id=user_data.get("id"), username=user_data.get("username")
                )if user_data else None,
                category=video.video_category,
            )
            for video in videos
        ]

        return response

    async def add_archive_or_remove(
        self, current_user: SUser, video_id: int, *args, **kwargs
    ):

        video_query = await self.session.execute(
            select(VideoModel)
            .filter(VideoModel.id == video_id)
            .filter(VideoModel.user_id == current_user.id)
        )


        video = video_query.scalars().first()

        if not video:
            return {
                "message": "Video not found or you do not have permission to modify it."
            }

        if video.is_exist:
            video.is_exist = False
        else:
            video.is_exist = True

        await self.session.commit()

    async def update_video(
        self,
        current_user: SUser,
        video_id: int,
        category: VideoCategory,
        video_title: str = Form(...),
        is_exist: bool = Form(...),
    ):

        video_query = await self.session.execute(
            select(VideoModel)
            .filter(VideoModel.id == video_id)
            .filter(VideoModel.user_id == current_user.id)
        )

        video = video_query.scalars().first()
        if not video:
            raise HTTPException(detail="Not Found", status_code=404)

        video.is_exist = is_exist
        video.video_title = video_title
        video.video_category = category

        await self.session.commit()

        return {"detail": "Updated Succsesfully"}
    



    async def like_video(self, video_id: int, current_user: SUser):
        video_query = await self.session.execute(select(VideoModel).filter(VideoModel.id == video_id))
        video = video_query.scalars().first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        existing_like = await self.session.execute(
            select(content_likes).filter_by(video_id=video_id, user_id=current_user.id)
        )
        
        if existing_like.first():
            raise HTTPException(status_code=400, detail="User has already liked this video")
        
        await self.session.execute(content_likes.insert().values(video_id=video_id, user_id=current_user.id))
        await self.session.commit()
        return {"message": "Video liked"}
    

    
    
    async def get_likes_from_video(self, current_user: SUser, video_id: int):

        likes_query = await self.session.execute(
            select(content_likes.c.user_id).filter_by(video_id=video_id)
        )

        likes = likes_query.scalars().all()

        if not likes:
            return []

        tasks = [
            self.send_request_to_kafka(user_id)  
            for user_id in likes
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        users = []

        for response in responses:
            if isinstance(response, Exception):
                log.warning(f"Error during request: {response}")
                continue

            user_data = response
            if not user_data:
                log.warning("Failed to get user data")
                continue

            users.append(SUser(
                id=user_data.get("id"),
                username=user_data.get("username")
            ))

        return users
    

    async def send_request_to_kafka(self, user_id: int):
        topic = 'fetch-user-data'
        message = {"user_id": user_id}

        try:
            await self.kafka_producer.send_and_wait(topic, value=str(message).encode('utf-8'))
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


    async def delete_video(self, current_user: SUser, video_id: int):

        video_query = await self.session.execute(
            select(VideoModel)
            .filter_by(id = video_id, user_id = current_user.id)
        )

        video = video_query.scalars().first()
        if not video:
            raise HTTPException(
                detail="Not Found",
                status_code=404
            )
        
        file_path = os.path.join(MEDIA_ROOT, str(video.video))
        os.remove(file_path)

        await self.session.delete(video)
        await self.session.commit()
        
        return {"Detail": f'video with id {video_id} deleted'}
    

    async def create_view(self, current_user: SUser, video_id: int):

        video_query = await self.session.execute(
            select(VideoModel)
            .filter(VideoModel.id == video_id)
        )

        video = video_query.scalars().first()
        if not video:
            raise HTTPException(
                detail=f"Not Found {video_id}",
                status_code=404
            )
        
        video.view_count  += 1
        self.session.add()
        await self.session.commit()

        return f"View Count {video.view_count}"
    