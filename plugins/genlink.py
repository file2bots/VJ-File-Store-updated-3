import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, NOTIFY_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
from plugins.imdb_api import get_poster  # Import IMDb poster fetching function
import os
import json
import requests
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from imdb import IMDb
imdb = IMDb()

async def get_poster(query, id=False):
    if not id:
        query = query.strip().lower()
        movie_list = imdb.search_movie(query)
        if not movie_list:
            return None
        movie = imdb.get_movie(movie_list[0].movieID)
    else:
        movie = imdb.get_movie(query)

    if not movie:
        return None

    return {
        'title': movie.get('title'),
        'year': movie.get('year'),
        'poster': movie.get('full-size cover url'),
        'plot': movie.get('plot outline', 'No description available.'),
        'url': f"https://www.imdb.com/title/tt{movie.movieID}/"
    }

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username
    file_type = message.media
    post = await message.copy(LOG_CHANNEL)
    file_id = str(post.id)
    
    # Extract title, quality, and language from file name
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else "Unknown"
    match = re.match(r"(.+?)\s*(\d{4})?\s*(\d+p)?\s*([a-zA-Z]+)?", file_name)
    if match:
        title = match.group(1).strip()
        year = match.group(2) if match.group(2) else "Unknown"
        quality = match.group(3) if match.group(3) else "Unknown"
        language = match.group(4) if match.group(4) else "Unknown"
    else:
        title, year, quality, language = "Unknown", "Unknown", "Unknown", "Unknown"
    
    # Fetch poster and IMDb data
    imdb_data = await get_poster(title, id=False)
    poster_url = imdb_data.get("poster", None)
    imdb_url = imdb_data.get("url", "")
    plot = imdb_data.get("plot", "No description available.")
    
    # Send notification to another channel
    notify_text = (f"**New File Added**\n\n🎬 **Title:** {title}\n📅 **Year:** {year}\n🖥 **Quality:** {quality}\n🗣 **Language:** {language}\n\n📖 **Plot:** {plot}\n🔗 [IMDb Link]({imdb_url})")
    
    if poster_url:
        await bot.send_photo(NOTIFY_CHANNEL, poster_url, caption=notify_text)
    else:
        await bot.send_message(NOTIFY_CHANNEL, notify_text)
    
    # Generate a short link and reply
    short_link = await get_short_link(file_id)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download", url=short_link)],[InlineKeyboardButton("🔄 Share", switch_inline_query=title)]])
    
    await message.reply_text(f"**Your file is ready:**\n🎬 **{title}**\n📥 [Download]({short_link})", reply_markup=reply_markup, disable_web_page_preview=True)
