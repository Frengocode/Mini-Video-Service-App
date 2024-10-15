from fastapi import FastAPI
from src.services.video_service.api import video_service_router
from fastapi.middleware.cors import CORSMiddleware
from src.services.video_service.database import Base, engine
from src.services.view_service.api import view_service 
from src.services.view_service.database import ViewBase
from src.services.comment_service.api import comment_service_router


app = FastAPI(title='Video Service')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=video_service_router)
app.include_router(router=view_service)
app.include_router(router=comment_service_router)




async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(ViewBase.metadata.create_all)




@app.on_event("startup")
async def on_startup():
    await create_tables()