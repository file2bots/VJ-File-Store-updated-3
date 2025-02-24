import motor.motor_asyncio
from config import DB_NAME, DB_URI
import re, base64, json
from struct import pack
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError

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

async def save_file(media):
    """Save file in the database."""
    
    file_id = unpack_new_file_id(media.file_id)
    file_name = clean_file_name(media.file_name)
    
    file = {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else None
    }

    if is_file_already_saved(file_id, file_name):
        return False, 0

    try:
        col.insert_one(file)
        print(f"{file_name} is successfully saved.")
        return True, 1
    except DuplicateKeyError:
        print(f"{file_name} is already saved.")
        return False, 0

def is_file_already_saved(file_id, file_name):
    """Check if the file is already saved in the database."""
    return bool(col.find_one({'file_id': file_id}) or col.find_one({'file_name': file_name}))

async def get_file_details(file_id):
    """Fetch file details by file_id."""
    return col.find_one({'file_id': file_id})

def unpack_new_file_id(new_file_id):
    """Convert Telegram's new file ID format to old format."""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id


db = Database(DB_URI, DB_NAME)
