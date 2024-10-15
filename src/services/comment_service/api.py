from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.kafka_server.main import get_kafka_producer
from src.uitils.auth import get_current_user
from src.services.comment_service.database import get_comment_service_session
from src.services.comment_service.service import CommentService, SUser, CommentResponse
from aiokafka import AIOKafkaProducer


comment_service_router = APIRouter(tags=["Comment Service"])


@comment_service_router.post("/create-comment/{video-id}")
async def create_comment(
    video_id: int,
    comment: str = Form(...),
    session: AsyncSession = Depends(get_comment_service_session),
    current_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = CommentService(
        session=session,
        kafka_client=kafka_client,
        comment_response=CommentResponse,
        auth_response=SUser,
    )
    return await service.create_comment(
        comment=comment, current_user=current_user, video_id=video_id
    )



@comment_service_router.get(
    "/comment-service/get-all-comments/{video_id}", response_model=list[CommentResponse]
)
async def get_all_comments(
    video_id: int,
    session: AsyncSession = Depends(get_comment_service_session),
    currenet_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = CommentService(
        session=session,
        comment_response=CommentResponse,
        auth_response=SUser,
        kafka_client=kafka_client,
    )
    return await service.get_all_comments(video_id=video_id, current_user=currenet_user)


@comment_service_router.delete(
    "/comment-service/delete-comment/{video_id}"
)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_comment_service_session),
    currenet_user: SUser = Depends(get_current_user),
    kafka_client: AIOKafkaProducer = Depends(get_kafka_producer),
):
    service = CommentService(
        session=session,
        comment_response=CommentResponse,
        auth_response=SUser,
        kafka_client=kafka_client,
    )
    return await service.delete_comment(comment_id=comment_id, current_user=currenet_user)
