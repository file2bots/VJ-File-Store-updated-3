import re
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import re
import os
import json
import base64
import requests
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from imdb import IMDb
from io import BytesIO
from PIL import Image
imdb = IMDb()
from imdb._exceptions import IMDbDataAccessError

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
    string = 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?start={outstr}"
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
        
    post = await replied.copy(LOG_CHANNEL)
    file_id = str(post.id)
    string = f"file_"
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?start={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

#OMDB_API_KEY = "7cd62fdc"

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
        l_chat_id = int(("-100" + l_chat_id))

    if f_chat_id != l_chat_id:
        return await message.reply("Chat ids not matched.")
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    
    sts = await message.reply("**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ**.\n**ᴛʜɪs ᴍᴀʏ ᴛᴀᴋᴇ ᴛɪᴍᴇ ᴅᴇᴘᴇɴᴅɪɴɢ ᴜᴘᴏɴ ɴᴜᴍʙᴇʀ ᴏғ ᴍᴇssᴀɢᴇs**")

    FRMT = "**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ...**\n**ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs:** {total}\n**ᴅᴏɴᴇ:** {current}\n**ʀᴇᴍᴀɪɴɪɴɢ:** {rem}\n**sᴛᴀᴛᴜs:** {sts}"

    outlist = []

    # file store without db channel
    og_msg = 0
    tot = 0
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if og_msg % 20 == 0:
            try:
                await sts.edit(FRMT.format(total=l_msg_id-f_msg_id, current=tot, rem=((l_msg_id-f_msg_id) - tot), sts="Saving Messages"))
            except:
                pass
        if msg.empty or msg.service:
            continue
        file = {
            "channel_id": f_chat_id,
            "msg_id": msg.id
        }
        og_msg +=1
        outlist.append(file)

    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)
    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️ Batch Generated For Filestore.")
    os.remove(f"batchmode_{message.from_user.id}.json")
    string = str(post.id)
    file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    user_id = message.from_user.id
    user = await get_user(user_id)
    if WEBSITE_URL_MODE == True:
        share_link = f"{WEBSITE_URL}?Tech_VJ=BATCH-{file_id}"
    else:
        share_link = f"https://t.me/{username}?start=BATCH-{file_id}"
    if user["base_site"] and user["shortener_api"] != None:
        short_link = await get_short_link(user, share_link)
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\nContains `{og_msg}` files.\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\nContains `{og_msg}` files.\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        
import base64
import json
import os
import re
import requests
from urllib.parse import quote_plus

from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.types import Message
from utils import get_shortlink, encode, humanbytes, get_name, get_hash, get_poster


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('post'))
async def post(client: Client, message: Message):
    try:
        num_files = await client.ask(
            text="<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴜsᴇ ᴏᴜʀ ʀᴀʀᴇ ᴍᴏᴠɪᴇ ᴘᴏsᴛ ғᴇᴀᴛᴜʀᴇ :) ᴄᴏᴅᴇᴅ ʙʏ <a href=https://t.me/NovaXTG>ɴᴏᴠᴀxᴛɢ</a> 👨🏼‍💻\n\n👉🏻 sᴇɴᴅ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ғɪʟᴇs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ 👈🏻\n\n‼️ ɴᴏᴛᴇ : ᴏɴʟʏ ɴᴜᴍʙᴇʀ</b>",
            chat_id=message.from_user.id, filters=filters.text, timeout=60,
            disable_web_page_preview=True
        )
        num_files = int(num_files.text)
    except Exception as e:
        print(f"Error in getting number of files: {e}")
        return

    media_list = []
    for i in range(num_files):
        try:
            forward_message = await client.ask(
                text=f"<b>⏩ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ɴᴏ : {i+1} ғɪʟᴇ</b>",
                chat_id=message.from_user.id, filters=(filters.video | filters.document), timeout=60
            )
        except Exception as e:
            print(f"Error in getting forward message: {e}")
            return
        
        post_message1 = await forward_message.copy(chat_id=CHANNEL_ID, disable_notification=True)
        post_message = await forward_message.copy(chat_id=BIN_CHANNEL, disable_notification=True)
        media = forward_message.document or forward_message.video
        media_list.append((media, post_message1.id, forward_message, post_message.id))
        await forward_message.delete()
        await forward_message.sent_message.delete()

    filename_message = await client.ask(
        text="<b>ɴᴏᴡ sᴇɴᴅ ᴛʜᴇ ɴᴀᴍᴇ ᴏғ ᴛʜᴇ ᴍᴏᴠɪᴇ\n\nᴇx : ᴀɴʙᴇ sɪᴠᴀᴍ (2003) ᴛᴀᴍɪʟ ʜᴅʀɪᴘ</b>",
        chat_id=message.from_user.id, filters=filters.text, timeout=60
    )
    filename = filename_message.text.strip() if filename_message else "Unknown Filename"
    await filename_message.sent_message.delete()
    await filename_message.delete()

    # Only generate a single batch link for all files
    batch_links = []

    # Process all the media files and prepare batch links
    for i, (media, msg_id, forward_message, post_message_id) in enumerate(media_list):
        string = f"get-{msg_id * abs(CHANNEL_ID)}"
        base64_string = await encode(string)
        file_size = humanbytes(media.file_size) if media.file_size else ""
        linkk = await get_shortlink(f"{RXL}/{base64_string}")
        link = f"<b>{file_size} :</b> {linkk}\n"
        batch_links.append(link)

    # Combine all batch links into a single string
    batch_links_string = '\n'.join(batch_links)

    # Construct unique stream links for the batch
    batch_stream_links = []
    batch_online_links = []

    for i, (media, msg_id, forward_message, post_message_id) in enumerate(media_list):
        online_linkk = await get_shortlink(f"{URL}{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  
        stream_linkk = await get_shortlink(f"{URL}watch/{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  
        stream_link = f"<b>{file_size} :</b> {stream_linkk}\n"
        online_link = f"<b>{file_size} :</b> {online_linkk}\n"
        batch_stream_links.append(stream_link)
        batch_online_links.append(online_link)

    # Join the stream links and online links
    batch_stream_links_string = '\n'.join(batch_stream_links)
    batch_online_links_string = '\n'.join(batch_online_links)

    # IMDb info fetching
    imdb_info = await get_poster(extract_movie_name(filename))
    
    # Check if IMDb info is found
    if imdb_info:
        # Download the IMDb poster image
        imdb_image_response = requests.get(imdb_info['poster'])
        imdb_image_data = io.BytesIO(imdb_image_response.content)
    else:
        # Use a default image if IMDb info is not found
        common_image_url = 'https://telegra.ph/file/74707bb075903640ed3f6.jpg'
        imdb_image_data = io.BytesIO(requests.get(common_image_url).content)

    # Send the IMDb poster image along with the batch links
    await client.send_photo(
        chat_id=message.chat.id,
        photo=imdb_image_data,
        caption=f'<b>🎬 {filename}\n\n'
                f'✅ Note : [ <a href=https://t.me/tnlinkdown/9>How to download</a> ]\n\n'
                f'🔻 Direct Telegram Files 🔻\n\n{batch_links_string}\n'
                f'🔻 Stream / Fast Download 🔻\n\n{batch_stream_links_string}\n'
                f'🔻 Online Links 🔻\n\n{batch_online_links_string}\n'
                f'@RX_LinkZz || @RolexMoviesOXO\n\n'
                f'Share and Support Us 🫶🏻</b>'
    )

#----------------------------------------------------------------------------------------------#
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

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  


def list_to_str(input_list):
    if not input_list:
        return "N/A"
    return ', '.join(str(element) for element in input_list)

def extract_movie_name(filename):
    # Updated pattern to capture movie name along with year and exclude anything after it
    pattern = r'(.+?\(\d{4}\)).*'
    match = re.match(pattern, filename)
    return match.group(1) if match else filename


