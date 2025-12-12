from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MASTER_DB = os.getenv("MASTER_DB", "org_master_db")

client = AsyncIOMotorClient(MONGO_URI)
master_db = client[MASTER_DB]


async def get_master_collection(name: str):
    return master_db[name]


# helper: ensure index for org collection
async def ensure_master_indexes():
    await master_db['organizations'].create_index('organization_name', unique=True)
    await master_db['admins'].create_index('email', unique=True)