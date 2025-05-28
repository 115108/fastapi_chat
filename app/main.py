from fastapi import FastAPI
from app.routers import chat, user

app = FastAPI()

# 路由注册
app.include_router(user.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}