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

import re
import json
import os
import base64
import requests
from pyrogram import Client, filters
from pyrogram.errors import (
    ChatAdminRequired, ChannelInvalid, UsernameInvalid, UsernameNotModified
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

OMDB_API_KEY = "YOUR_OMDB_API_KEY"
LOG_CHANNEL = "YOUR_LOG_CHANNEL"

title_requests = {}  # Store pending title requests


@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username

    # Validate input format
    args = message.text.split(" ")
    if len(args) != 3:
        return await message.reply("⚠️ **Incorrect format.**\nExample: `/batch <link1> <link2>`")

    _, first, last = args
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    # Validate first link
    match_first = regex.match(first)
    if not match_first:
        return await message.reply("❌ **Invalid first link!**")

    f_chat_id, f_msg_id = match_first.group(4), int(match_first.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int("-100" + f_chat_id)

    # Validate last link
    match_last = regex.match(last)
    if not match_last:
        return await message.reply("❌ **Invalid last link!**")

    l_chat_id, l_msg_id = match_last.group(4), int(match_last.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int("-100" + l_chat_id)

    # Ensure both links belong to the same chat
    if f_chat_id != l_chat_id:
        return await message.reply("❌ **Links must be from the same channel!**")

    # Validate access to the chat
    try:
        chat = await bot.get_chat(f_chat_id)
        chat_id = chat.id
        if not chat.has_protected_content:
            await bot.get_chat_member(chat_id, "me")
    except ChatAdminRequired:
        return await message.reply("❌ **I need admin rights in this channel!**")
    except ChannelInvalid:
        return await message.reply("❌ **Invalid channel. Add me as an admin.**")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("❌ **Invalid link provided!**")
    except Exception as e:
        return await message.reply(f"❌ **Error:** `{e}`")

    # Fetch messages
    sts = await message.reply("⏳ **Fetching messages... Please wait!**")
    outlist = []
    count = 0

    async for msg in bot.iter_messages(f_chat_id, min_id=f_msg_id-1, max_id=l_msg_id+1, reverse=True):
        if msg.empty or msg.service:
            continue
        outlist.append({"channel_id": chat_id, "msg_id": msg.id})
        count += 1

    # If no messages found
    if not outlist:
        return await sts.edit("❌ **No valid messages found in the given range!**")

    # Save to JSON file
    json_file = f"batch_{message.from_user.id}.json"
    with open(json_file, "w") as out:
        json.dump(outlist, out)

    # Send JSON file
    post = await bot.send_document(LOG_CHANNEL, json_file, file_name="Batch.json", caption="✅ **Batch Generated.**")
    os.remove(json_file)

    # Generate batch link
    file_id = base64.urlsafe_b64encode(str(post.id).encode()).decode().strip("=")
    share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

    # Ask user for title and year
    title_request_msg = await sts.edit(
        f"✅ **Batch Link Created!**\n\n🔗 **Link:** {share_link}\n\n"
        "📌 **Now, send me the title and year like this:**\n"
        "`Movie Title | Year`"
    )

    # Store request details
    title_requests[message.from_user.id] = {
        "message_id": title_request_msg.message_id,
        "share_link": share_link
    }


@Client.on_message(filters.text & filters.reply)
async def get_title_year(bot, title_msg):
    user_id = title_msg.from_user.id
    if user_id not in title_requests:
        return  # Ignore unrelated messages

    request_data = title_requests[user_id]
    expected_message_id = request_data["message_id"]
    share_link = request_data["share_link"]

    # Validate reply context
    if title_msg.reply_to_message.message_id != expected_message_id:
        return

    # Validate title format
    if "|" not in title_msg.text:
        return await title_msg.reply("❌ **Invalid format!**\nUse: `Movie Title | Year`")

    title, year = map(str.strip, title_msg.text.split("|"))

    # Fetch poster from OMDb
    url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    poster_url = response.get("Poster") if response.get("Response") == "True" else None
    imdb_id = response.get("imdbID")

    # Create inline buttons
    buttons = [
        [InlineKeyboardButton("🎬 Watch Now", url=share_link)]
    ]
    if imdb_id:
        buttons.append([InlineKeyboardButton("🔍 More Info", url=f"https://www.imdb.com/title/{imdb_id}")])

    caption = f"🎬 **{title} ({year})**\n\n🔗 **Link:** {share_link}"

    # Send movie post
    if poster_url:
        await bot.send_photo(title_msg.chat.id, poster_url, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await bot.send_message(title_msg.chat.id, caption, reply_markup=InlineKeyboardMarkup(buttons))

    await title_msg.reply("✅ **Post created successfully!**")

    # Remove user entry
    del title_requests[user_id]
