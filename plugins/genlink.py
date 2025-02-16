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

OMDB_API_KEY = "7cd62fdc"

@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username

    if " " not in message.text:
        return await message.reply("Use correct format.\nExample /batch https://t.me/CloudXbotz/41 https://t.me/CloudXbotz/42.")

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample /batch https://t.me/CloudXbotz/41 https://t.me/CloudXbotz/42.")

    cmd, first, last = links
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')

    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int("-100" + f_chat_id)

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
    except ChannelInvalid:
        return await message.reply('This may be a private channel. Make me an admin to index files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Error - {e}')
    
    sts = await message.reply("**Generating link... Please wait!**")

    outlist = []
    tot = 0
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        tot += 1
        if msg.empty or msg.service:
            continue
        file = {"channel_id": f_chat_id, "msg_id": msg.id}
        outlist.append(file)

    json_file = f"batchmode_{message.from_user.id}.json"
    with open(json_file, "w+") as out:
        json.dump(outlist, out)

    post = await bot.send_document(LOG_CHANNEL, json_file, file_name="Batch.json", caption="⚠️ Batch Generated.")
    os.remove(json_file)

    file_id = base64.urlsafe_b64encode(str(post.id).encode("ascii")).decode().strip("=")
    share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

    title_request = await sts.edit(
        f"✅ **Batch Link Generated!**\n\n🔗 **Link:** {share_link}\n\n📌 **Now, send me the title and year in this format:**\n`Title | Year`"
    )

    # **WAIT FOR TITLE & YEAR INPUT**
    @Client.on_message(filters.text & filters.reply)
    async def get_title_year(bot, title_msg):
        if title_msg.reply_to_message.message_id != title_request.message_id:
            return  # Ignore unrelated messages

        if "|" not in title_msg.text:
            return await title_msg.reply("❌ Invalid format. Send like this: `Inception | 2010`")

        title, year = map(str.strip, title_msg.text.split("|"))

        # **FETCH POSTER FROM OMDb**
        url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
        response = requests.get(url).json()
        if response.get("Response") == "True":
            poster_url = response.get("Poster", None)
        else:
            poster_url = None

        # **CREATE POST WITH INLINE BUTTON**
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Watch Now", url=share_link)],
            [InlineKeyboardButton("🔍 More Info", url=f"https://www.imdb.com/title/{response.get('imdbID')}")] if response.get("imdbID") else []
        ])

        caption = f"🎬 **{title} ({year})**\n\n🔗 **Link:** {share_link}"
        
        if poster_url:
            await bot.send_photo(message.chat.id, poster_url, caption=caption, reply_markup=buttons)
        else:
            await bot.send_message(message.chat.id, caption, reply_markup=buttons)

        await title_msg.reply("✅ **Post created successfully!**")
