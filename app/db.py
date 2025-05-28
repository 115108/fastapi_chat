from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://slue31907:Sl_115108@chat.0o4ear0.mongodb.net/chat_db?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URI)

db = client["chat_app"]  