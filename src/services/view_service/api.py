from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.kafka_server.main import get_kafka_producer
from src.services.view_service.service import (
    ViewService,
    SUser,
    VideoReponse,
    ViewResponse,
)
from src.uitils.auth import get_current_user
from src.services.view_service.database import get_view_service_session
from aiokafka import AIOKafkaProducer

view_service = APIRouter(tags=["View Service"])


@view_service.post("/view-service/create-view/{video_id}")
async def create_view(
    video_id: int,
    session: AsyncSession = Depends(get_view_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = ViewService(session=session, kafka_client=kafka_producer)
    return await service.create_view_for_video(
        video_id=video_id, current_user=current_user
    )


@view_service.get(
    "/view-service/get-all-user-viewed-videos", response_model=list[ViewResponse]
)
async def get_all_viwed_video(
    session: AsyncSession = Depends(get_view_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = ViewService(session=session, kafka_client=kafka_producer)
    return await service.get_user_viewed_video(current_user=current_user)


@view_service.delete("/view-service/delete-view/{view_id}")
async def delete_view(
    view_id: int,
    session: AsyncSession = Depends(get_view_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = ViewService(session=session, kafka_client=kafka_client)
    return await service.delete_view(view_id=view_id, current_user=current_user)
