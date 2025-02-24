import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
from datetime import date, datetime
from config import SHORTLINK_API, SHORTLINK_URL, POST_SHORT_API, POST_SHORT_URL, POST_MODE, DIRECT_GEN, DIRECT_GEN_URL, DIRECT_GEN_DB
from shortzy import Shortzy
from imdb import Cinemagoer 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

imdb = Cinemagoer() 
TOKENS = {}
VERIFIED = {}

class temp(object):
    IMDB_CAP = {}


async def get_verify_shorted_link(link):
    if SHORTLINK_URL == "api.shareus.io":
        url = f'https://{SHORTLINK_URL}/easy_api'
        params = {
            "key": SHORTLINK_API,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(e)
            return link
    else:
  #      response = requests.get(f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={link}")
 #       data = response.json()
  #      if data["status"] == "success" or rget.status_code == 200:
   #         return data["shortenedUrl"]
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        link = await shortzy.convert(link)
        return link

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False

async def get_token(bot, userid, link):
    user = await bot.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    shortened_verify_url = await get_verify_shorted_link(link)
    return str(shortened_verify_url)

async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    VERIFIED[user.id] = str(today)

async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            return False
        else:
            return True
    else:
        return False

#------------------------------------Post Code--------------------------------------------------#
#POST FEATURES 

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{str(round(size, 2))} {Dic_powerN[n]}B"

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def get_media_from_message(message: "Message") :
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media
            
def clean_title(title_clean):
    # Regular expression to match the title and year with optional text afterwards
    match = re.match(r'^(.*?)(\d{4})(?:\s.*|$)', title_clean, re.IGNORECASE)
    if match:
        
        title_cleaned = match.group(1).strip()
        year = match.group(2).strip()
        return f"{title_cleaned.capitalize()} {year}"  
    return title_clean 

def get_name(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return str(getattr(media, "file_name", "None"))

def get_hash(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

async def gen_link(log_msg: Message):
    """Generate Text for Stream Link, Reply Text and reply_markup
    r : return page_link, stream_link
    page_link : stream page link
    stream_link : download link
    """
    page_link = f"{DIRECT_GEN_URL}watch/{get_hash(log_msg)}{log_msg.id}"
    stream_link = f"{DIRECT_GEN_URL}{log_msg.id}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
    # short    
    return page_link, stream_link

async def short_link(link):
    if not POST_MODE:
        return link
    # Replace the placeholders with your actual API key and base URL
    api_key = POST_SHORT_API
    base_site = POST_SHORT_URL

    if not (api_key and base_site):
        return link

    shortzy = Shortzy(api_key, base_site)
    short_link = await shortzy.convert(link)

    return short_link

async def delete_previous_reply(chat_id):
    if chat_id in user_states and "last_reply" in user_states[chat_id]:
        try:
            await user_states[chat_id]["last_reply"].delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
