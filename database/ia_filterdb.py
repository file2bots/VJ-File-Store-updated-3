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

async def add_name(user_id, filename):
    user_db = mydb[str(user_id)]
    user = {'_id': filename}
    existing_user = user_db.find_one({'_id': filename})
    if existing_user is not None:
        return False
    try:
        user_db.insert_one(user)
        return True
    except DuplicateKeyError:
        return False
      
async def delete_all_msg(user_id):
    user_db = mydb[str(user_id)]
    user_db.delete_many({})

#---------------------------auto Movie Update---------------------------#
import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from config import DB_URI, DB_NAME, DEENDAYAL_MOVIE_UPDATE_CHANNEL, OWNERID, CUSTOM_FILE_CAPTION
from utils import temp
from .Imdbposter import get_movie_details, fetch_image
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#---------------------------------------------------------
# Some basic variables needed
tempDict = {'indexDB': DB_URI}

# Primary DB
client = AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]
instance = Instance.from_db(db)

# Primary DB Model
@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

async def save_file(bot, media):
    """Save file in database"""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    
    try:
        if await Media.count_documents({'file_id': file_id}, limit=1):
            logger.warning(f'{file_name} is already saved in database!')
            return False, 0

        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(f'{file_name} is already saved in database')   
            return False, 0
        else:
            logger.info(f'{file_name} is saved to database')
            if await get_status(bot.me.id):
                await send_msg(bot, file.file_name, file.caption)
            return True, 1


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0):
    """For given query return (results, next_offset)"""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            max_results = 10 if settings['max_btn'] else int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            max_results = 10 if settings['max_btn'] else int(MAX_B_TN)

    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_()]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    filter = {'$or': [{'file_name': regex}, {'caption': regex}]} if CUSTOM_FILE_CAPTION else {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)

    if max_results % 2 != 0: 
        logger.info(f"Since max_results is an odd number ({max_results}), bot will use {max_results+1} as max_results to make it even.")
        max_results += 1

    cursor = Media.find(filter).sort('$natural', -1).skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    next_offset = offset + len(files)
    if next_offset >= total_results:
        next_offset = ''

    return files, next_offset, total_results


async def get_bad_files(query, file_type=None):
    """For given query return (results, total_results)"""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_()]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    filter = {'$or': [{'file_name': regex}, {'caption': regex}]} if USE_CAPTION_FILTER else {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    cursor = Media.find(filter).sort('$natural', -1)
    files = await cursor.to_list(length=await Media.count_documents(filter))

    total_results = len(files)

    return files, total_results


async def get_file_details(query):
    """Retrieve file details from database"""
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails



def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
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
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref


async def send_msg(bot, filename, caption): 
    try:
        filename = re.sub(r'\(\@\S+\)|\[\@\S+\]|\b@\S+|\bwww\.\S+', '', filename).strip()
        caption = re.sub(r'\(\@\S+\)|\[\@\S+\]|\b@\S+|\bwww\.\S+', '', caption).strip()
        
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None

        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption) or re.search(pattern, filename)
        season = season.group(1) if season else None 

        if year:
            filename = filename[: filename.find(year) + 4]  
        elif season and season in filename:
            filename = filename[: filename.find(season) + 1]

        qualities = ["ORG", "org", "hdcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", "camrip", "CAMRip", "hdtc", "predvd", "DVDscr", "dvdscr", "dvdrip", "dvdscr", "HDTC", "dvdscreen", "HDTS", "hdts"]
        quality = await get_qualities(caption.lower(), qualities) or "HDRip"

        language = ""
        possible_languages = CAPTION_LANGUAGES
        for lang in possible_languages:
            if lang.lower() in caption.lower():
                language += f"{lang}, "
        language = language[:-2] if language else "Not idea 😄"

        filename = re.sub(r"[\(\)\[\]\{\}:;'\-!]", "", filename)

        text = "#𝑵𝒆𝒘_𝑭𝒊𝒍𝒆_𝑨𝒅𝒅𝒆𝒅 ✅\n\n👷𝑵𝒂𝒎𝒆: `{}`\n\n🌳𝑸𝒖𝒂𝒍𝒊𝒕𝒚: {}\n\n🍁𝑨𝒖𝒅𝒊𝒐: {}"
        text = text.format(filename, quality, language)

        if await add_name(OWNERID, filename):
            imdb = await get_movie_details(filename)  
            resized_poster = None

            if imdb:
                poster_url = imdb.get('poster_url')
                if poster_url:
                    resized_poster = await fetch_image(poster_url)  

            filenames = filename.replace(" ", '-')
            btn = [[InlineKeyboardButton('🌲 Get Files 🌲', url=f"https://telegram.me/{temp.U_NAME}?start=getfile-{filenames}")]]
            
            if resized_poster:
                await bot.send_photo(chat_id=DEENDAYAL_MOVIE_UPDATE_CHANNEL, photo=resized_poster, caption=text, reply_markup=InlineKeyboardMarkup(btn))
            else:              
                await bot.send_message(chat_id=DEENDAYAL_MOVIE_UPDATE_CHANNEL, text=text, reply_markup=InlineKeyboardMarkup(btn))

    except:
        pass

async def get_qualities(text, qualities: list):
    """Get all Quality from text"""
    quality = []
    for q in qualities:
        if q in text:
            quality.append(q)
    quality = ", ".join(quality)
    return quality[:-2] if quality.endswith(", ") else quality
#------------------------------End Auto Post Code------------------------------#


# Initialize the single database instance
db = Database(DB_URI, DB_NAME)
