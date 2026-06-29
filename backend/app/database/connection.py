from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

# Global database client
mongodb_client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    global mongodb_client, database
    import certifi
    
    mongodb_client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        tlsCAFile=certifi.where()
    )
    database = mongodb_client[settings.DATABASE_NAME]
    
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")



async def close_mongo_connection():
    """Close MongoDB connection."""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return database
