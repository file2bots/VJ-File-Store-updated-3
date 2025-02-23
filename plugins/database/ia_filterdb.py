import re, base64, json
from struct import pack
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from config import DB_URI, DB_NAME, COLLECTION_NAME  # Ensure COLLECTION_NAME is in config

# Connect to MongoDB
client = MongoClient(DB_URI)
db = client[DB_NAME]
col = db[COLLECTION_NAME]  # Define collection

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

async def get_search_results(query, max_results=10, offset=0):
    """Return search results."""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]') 

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        regex = query

    filter_criteria = {'file_name': regex}
    cursor = col.find(filter_criteria).sort('$natural', -1).skip(offset).limit(max_results)
    
    files = list(cursor)
    total_results = col.count_documents(filter_criteria)
    next_offset = "" if (offset + max_results) >= total_results else (offset + max_results)

    return files, next_offset, total_results

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
