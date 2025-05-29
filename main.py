from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(user.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}