# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import re
import os
import json
import base64

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username
    file_type = message.media
    post = await message.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        

@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message
    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    post = await replied.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = f"file_"
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

import re
import os
import json
import base64
import io
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from imdb import IMDb
from PIL import Image
imdb = IMDb()
from imdb._exceptions import IMDbDataAccessError


# Store temporary data for user input
pending_movies = {}


def extract_movie_name(filename):
    """Extracts movie name from a filename (dummy function, implement as needed)."""
    return filename.rsplit(".", 1)[0]  # Replace with a proper extraction method

@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample /batch https://t.me/vj_botz/10 https://t.me/vj_botz/20.")
    cmd, first, last = links
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int(("-100" + f_chat_id))
    
    match = regex.match(last)
    if not match:
        return await message.reply('Invalid link')
    
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int("-100" + l_chat_id)

    if f_chat_id != l_chat_id:
        return await message.reply("Chat IDs do not match.")
    
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except Exception as e:
        return await message.reply(f'Error - {e}')
    
    sts = await message.reply("Generating batch link...")

    outlist = []
    og_msg = 0
    tot = 0
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if og_msg % 20 == 0:
            try:
                await sts.edit(f"Processing messages: {tot}/{l_msg_id - f_msg_id}")
            except:
                pass
        if msg.empty or msg.service:
            continue
        file = {"channel_id": f_chat_id, "msg_id": msg.id}
        og_msg += 1
        outlist.append(file)

    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)
    
    post = await bot.send_document(
        LOG_CHANNEL, f"batchmode_{message.from_user.id}.json",
        file_name="Batch.json", caption="⚠️ Batch Generated For Filestore."
    )
    
    os.remove(f"batchmode_{message.from_user.id}.json")
    string = str(post.id)
    file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    
    user_id = message.from_user.id
    if WEBSITE_URL_MODE:
        batch_link = f"{WEBSITE_URL}?Tech_VJ=BATCH-{file_id}"
    else:
        batch_link = f"https://t.me/{username}?start=BATCH-{file_id}"

    pending_movies[user_id] = {
        "share_link": batch_link,
        "file_count": og_msg,
        "message": message
    }

    await sts.edit("✅ Batch link generated! Now send me the **movie title** and **year** in this format:\n\n`Title (Year)`")

@Client.on_message(filters.text & filters.private)
async def receive_movie_details(bot, message):
    user_id = message.from_user.id
    if user_id not in pending_movies:
        return
    
    movie_data = pending_movies.pop(user_id)
    batch_link = movie_data["batch_link"]
    file_count = movie_data["file_count"]

    # Extract title and year
    if "(" in message.text and ")" in message.text:
        title, year = message.text.rsplit("(", 1)
        title = title.strip()
        year = year.replace(")", "").strip()
    else:
        return await message.reply("Invalid format! Please send as `Title (Year)`.")

    # Get IMDb poster
    imdb_info = await get_poster(extract_movie_name(title))
    if imdb_info and "poster" in imdb_info:
        imdb_image_url = imdb_info["poster"]
    else:
        imdb_image_url = 'https://telegra.ph/file/74707bb075903640ed3f6.jpg'  # Default poster

    imdb_image_data = io.BytesIO(requests.get(imdb_image_url).content)

    # Send post with inline button
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=imdb_image_data,
        caption=f"🎬 **Movie Title:** {title}\n📅 **Year:** {year}\n📁 **Total Files:** {file_count}\n\n👇 Click the button below to access the files!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"{title} ({year})", url=batch_link)]]
        )
    )


#---------------------------------IMDB--------------------------------------#

async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = query.strip().lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not True:  # Replace True with the condition you want
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }


@Bot.on_message(filters.command('imdb') & filters.private)
async def imdb_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a movie name with the /imdb command.")
        return

    movie_name = ' '.join(message.command[1:])
    
    try:
        poster_info = await get_poster(movie_name)
        
        if poster_info:
            # Download the poster image
            image_response = requests.get(poster_info['poster'])
            image_data = io.BytesIO(image_response.content)

            # Send the poster image as a photo along with other details
            await client.send_photo(
                chat_id=message.chat.id,
                photo=image_data,
                caption=f'Movie Poster for {poster_info["title"]}\n'
                        f'Rating: {poster_info["rating"]}\n'
                        f'Genres: {poster_info["genres"]}\n'
                        f'Plot: {poster_info["plot"]}\n'
                        f'IMDb URL: {poster_info["url"]}'
            )

        else:
            await message.reply_text('Movie not found. Please check the movie name and try again.')

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply_text('An error occurred while fetching movie information.')
