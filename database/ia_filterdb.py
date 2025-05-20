import motor.motor_asyncio
import re
from config import DB_NAME, DB_URI

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.files

    def new_user(self, id, name):
        return dict(id=id, name=name)
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def save_file(self, media):
        """Save file in the database."""
        file_id = unpack_new_file_id(media.file_id)  # Now returns file_id directly
        file_name = clean_file_name(media.file_name)
        
        file = {
            'file_id': file_id,
            'file_name': file_name,
            'file_size': media.file_size,
            'caption': media.caption.html if media.caption else None
        }
        
        if await self.is_file_already_saved(file_id, file_name):
            return False, 0

        try:
            await self.col.insert_one(file)
            print(f"{file_name} is successfully saved.")
            return True, 1
        except:
            print("Error saving file.")
            return False, 0
    
    async def is_file_already_saved(self, file_id, file_name):
        """Check if the file is already saved."""
        found1 = {'file_name': file_name}
        found = {'file_id': file_id}

        if await self.col.find_one(found1) or await self.col.find_one(found):
            print(f"{file_name} is already saved.")
            return True
        
        return False
    
    async def get_search_results(self, query, max_results=10, offset=0):
        """For given query return (results, next_offset)"""
        query = query.strip()
        raw_pattern = r'(|[.+-_])' + query + r'(|[.+-_])' if query else '.'
        
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            regex = query

        filter = {'file_name': regex}
        cursor = self.col.find(filter).sort('$natural', -1).skip(offset).limit(max_results)
        files = [file async for file in cursor]
        
        total_results = await self.col.count_documents(filter)
        next_offset = "" if (offset + max_results) >= total_results else (offset + max_results)

        return files, next_offset, total_results
    
    async def get_file_details(self, file_id):
        return await self.col.find_one({'file_id': file_id})

def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name)) 
    unwanted_chars = ['[', ']', '(', ')', '{', '}']
    
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
        
    return ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.') and not x.startswith('t.me'), file_name.split()))

def unpack_new_file_id(new_file_id):
    """Return file_id directly from Pyrogram v2.0+"""
    return new_file_id  # No need to decode/re-encode

    async def get_files_by_query(query):
        from . import media_collection  # Make sure you’ve initialized this MongoDB collection
    
        # Search by title or filename
        results = media_collection.find({
            "$text": {"$search": query}
        })
    
        files = []
        async for doc in results:
            files.append(doc)
        return files


# Initialize the single database instance
db = Database(DB_URI, DB_NAME)


