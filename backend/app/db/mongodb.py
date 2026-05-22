from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URL)
    mongodb.db = mongodb.client.get_default_database()

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
