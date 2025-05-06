#db.py, MongoDB 연결

from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.welfare
policies = db.policies
extra_info = db.extra_info