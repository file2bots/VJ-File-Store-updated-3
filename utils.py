import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
import math
from datetime import date, datetime
from config import *
from shortzy import Shortzy
from urllib.parse import quote_plus
from pyrogram.types import Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TOKENS = {}
VERIFIED = {}

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
        
#-------------------------------------IMDB POSTER----------------------------------------#

from imdb import Cinemagoer
from bs4 import BeautifulSoup

imdb = Cinemagoer()

class temp(object):
    IMDB_CAP = {}
    U_NAME = None
    B_NAME = None


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    else:
        return ', '.join(str(elem) for elem in k)

async def get_poster(query, bulk=False, id=False, file=None):
    if not query:
        print("get_poster: Empty or None query received")
        return None

    query = query.strip().lower()
    title = query
    year = None

    # Extract year from query or filename if possible
    import re
    year_match = re.findall(r'[1-2]\d{3}$', query)
    if year_match:
        year = year_match[0]
        title = query.replace(year, "").strip()
    elif file:
        year_match = re.findall(r'[1-2]\d{3}', file)
        if year_match:
            year = year_match[0]

            # Search movie by title
            movie_search = imdb.search_movie(title, results=10)
            if not movie_search:
                print("No movie found for query:", title)
                return None

            # Filter by year if given
            if year:
                filtered = [m for m in movie_search if str(m.get('year')) == year]
                if not filtered:
                    filtered = movie_search
            else:
                filtered = movie_search

            # Filter by kind movie or tv series
            filtered = [m for m in filtered if m.get('kind') in ['movie', 'tv series']]
            if not filtered:
                filtered = movie_search

            if bulk:
                return filtered
            movieid = filtered[0].movieID
        else:
            movieid = query

        movie = imdb.get_movie(movieid)
        if not movie:
            print("No movie details found for ID:", movieid)
            return None

        # Get release date or year
        release_date = movie.get('original air date') or movie.get('year') or "N/A"

        # Get plot (limit length)
        plot = movie.get('plot outline') or (movie.get('plot')[0] if movie.get('plot') else "")
        if plot and len(plot) > 800:
            plot = plot[:800] + "..."

        # Get poster url, try fallback if missing
        poster_url = movie.get('full-size cover url') or movie.get('cover url') or ""
        if not poster_url and movie.get('imdbID'):
            imdb_id = movie.get('imdbID')
            # This is a common poster base url pattern for IMDb, but not guaranteed
            poster_url = f"https://m.media-amazon.com/images/M/{imdb_id}.jpg"

        # Debug print
        print(f"Poster URL for {movie.get('title')}: {poster_url}")

        return {
            'title': movie.get('title'),
            'votes': movie.get('votes'),
            'aka': list_to_str(movie.get('akas')),
            'seasons': movie.get('number of seasons'),
            'box_office': movie.get('box office'),
            'localized_title': movie.get('localized title'),
            'kind': movie.get('kind'),
            'imdb_id': f"tt{movie.get('imdbID')}",
            'cast': list_to_str(movie.get('cast')),
            'runtime': list_to_str(movie.get('runtimes')),
            'countries': list_to_str(movie.get('countries')),
            'certificates': list_to_str(movie.get('certificates')),
            'languages': list_to_str(movie.get('languages')),
            'director': list_to_str(movie.get('director')),
            'writer': list_to_str(movie.get('writer')),
            'producer': list_to_str(movie.get('producer')),
            'composer': list_to_str(movie.get('composer')),
            'cinematographer': list_to_str(movie.get('cinematographer')),
            'music_team': list_to_str(movie.get('music department')),
            'distributors': list_to_str(movie.get('distributors')),
            'release_date': release_date,
            'year': movie.get('year'),
            'genres': list_to_str(movie.get('genres')),
            'poster': poster_url,
            'plot': plot,
            'rating': str(movie.get('rating')),
            'url': f'https://www.imdb.com/title/tt{movieid}'
        }

    except Exception as e:
        print(f"Error in get_poster: {e}")
        return None
        
async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all( 'h3' )
    return [title.getText() for title in titles]

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

#------------------------------------------------------
#POST FEATURES 

def humanbytes(size):
    """Convert bytes to a human-readable format, rounding up."""
    
    if not size:
        return ""
    
    power = 2**10
    n = 0
    Dic_powerN = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    
    while size > power and n < len(Dic_powerN) - 1:
        size /= power
        n += 1
    
    return f"{math.ceil(size)} {Dic_powerN[n]}B"

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

def get_size(size):
    """Get size in a human-readable format, rounded up."""
    
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0

    while size >= 1024.0 and i < len(units) - 1:
        i += 1
        size /= 1024.0

    return f"{math.ceil(size)} {units[i]}"
