from fastapi import APIRouter, Depends, UploadFile, File, Form, responses, HTTPException
from .service import (
    VideoModelService,
    get_current_user,
    AsyncSession,
    VideoCategory,
    SUser,
    VideoReponse,
    MEDIA_ROOT
)
from src.services.video_service.database import get_video_service_session
from aiokafka import AIOKafkaProducer
from src.kafka_server.main import get_kafka_producer
import aiofiles
import os


video_service_router = APIRouter(tags=["Video Service"])


@video_service_router.post("/video-service/create-video/")
async def create_video(
    category: VideoCategory,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    title: str = Form(...),
    video: UploadFile = File(...),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_client)
    video_category = category.value
    return await service.create_video(
        title=title, current_user=current_user, category=video_category, video=video
    )



@video_service_router.post("/video-service/create-view/{video_id}")
async def create_view(video_id: int, session: AsyncSession = Depends(get_video_service_session), current_user: SUser = Depends(get_current_user), kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    service = VideoModelService(session=session, kafka_producer=kafka_producer)
    return await service.create_view(video_id=video_id, current_user=current_user)




@video_service_router.get(
    "/video-service/get-all-video/", response_model=list[VideoReponse]
)
async def get_all_videos(
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer = kafka_client)
    return await service.get_all_video(current_user=current_user)


@video_service_router.get(
    "/video-service/get-video/{video_id}", response_model=VideoReponse
)
async def get_video(
    video_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer = kafka_client)
    return await service.get_video_with_id(video_id=video_id)


@video_service_router.get(
    "/video-service/get-video-by-category", response_model=list[VideoReponse]
)
async def get_video(
    category: VideoCategory,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer = kafka_client)
    video_category = category.value
    return await service.get_video_by_category(
        category=video_category, current_user=current_user
    )


@video_service_router.get(
    "/get-all-user-videos/{user_id}/", response_model=list[VideoReponse]
)
async def get_all_user_videos(
    user_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_client)
    return await service.get_all_user_videos(user_id=user_id, current_user=current_user)


@video_service_router.patch("/video-service/add-archive-or-remove/{video_id}")
async def add_video_to_archive_or_remove(
    video_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_client)
    return await service.add_archive_or_remove(
        video_id=video_id, current_user=current_user
    )


@video_service_router.patch("/update-video/{video_id}")
async def update_video(
    video_id: int,
    category: VideoCategory,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    video_title: str = Form(...),
    is_exist: bool = Form(...),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_client)
    video_category = category.value
    return await service.update_video(
        video_id=video_id,
        current_user=current_user,
        video_title=video_title,
        is_exist=is_exist,
        category=video_category,
    )


@video_service_router.post("/video_service/like/{video_id}")
async def like_btn(
    video_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_client)
    return await service.like_video(video_id=video_id, current_user=current_user)


@video_service_router.get(
    "/video-service/get-likes-from/{video_id}", response_model=list[SUser]
)
async def get_likes_from(
    video_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_procuer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = VideoModelService(session=session, kafka_producer=kafka_procuer)
    return await service.get_likes_from_video(
        video_id=video_id, current_user=current_user
    )


@video_service_router.delete("/video-service/delete-video/{video_id}")
async def delete_video(
    video_id: int,
    session: AsyncSession = Depends(get_video_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    service = VideoModelService(session=session, kafka_producer=kafka_producer)
    return await service.delete_video(video_id=video_id, current_user=current_user)


@video_service_router.get("/video-service/get-video-file/{filename}")
async def get_video_file(filename: str):
    file_path = os.path.join(MEDIA_ROOT, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    async def file_streamer(file_path):
        async with aiofiles.open(file_path, mode='rb') as file:
            chunk_size = 1024 * 1024 
            while chunk := await file.read(chunk_size):
                yield chunk
    
    return responses.StreamingResponse(file_streamer(file_path), media_type="video/mp4")

