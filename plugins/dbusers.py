import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.user_col = self.db.users
        self.file_col = self.db.files  # New collection for storing files

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.user_col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.user_col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.user_col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.user_col.find({})

    async def delete_user(self, user_id):
        await self.user_col.delete_many({'id': int(user_id)})

    # ✅ NEW: Function to add file details to the database
    async def add_file(self, file_id, title, year, quality, language, imdb_url, poster_url):
        file_data = {
            "file_id": file_id,
            "title": title,
            "year": year,
            "quality": quality,
            "language": language,
            "imdb_url": imdb_url,
            "poster_url": poster_url
        }
        await self.file_col.insert_one(file_data)

    # ✅ NEW: Get file details from database
    async def get_file(self, file_id):
        return await self.file_col.find_one({"file_id": file_id})

    # ✅ NEW: Delete file from database
    async def delete_file(self, file_id):
        await self.file_col.delete_many({"file_id": file_id})

db = Database(DB_URI, DB_NAME)
