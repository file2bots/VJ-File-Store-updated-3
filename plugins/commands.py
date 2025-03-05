# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import logging
import random
import asyncio
import logging  # Ensure logging is imported
import re
import json
import base64
from urllib.parse import quote_plus

from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *

# Lazy import to prevent circular dependency
from config import *

# Import utils functions separately to avoid circular import
from utils import (
    verify_user, check_token, check_verification, get_token, get_size,
    gen_link, clean_title, get_poster, temp, short_link
)

# Import TechVJ utilities safely
from CloudXbotz.utils.file_properties import get_name, get_hash, get_media_file_size

# Initialize logger
logger = logging.getLogger(__name__)

BATCH_FILES = {}

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01


def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def formate_file_name(file_name):
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ0


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    username = client.me.username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
            ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
            ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        me = client.me
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, me.mention),
            reply_markup=reply_markup
        )
        return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
    elif data.split("-", 1)[0] == "BATCH":
        try:
            if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
                ],[
                    InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                ]]
                await message.reply_text(
                    text="<b>You are not verified !\nKindly verify to continue !</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            return await message.reply_text(f"**Error - {e}**")
        sts = await message.reply("**🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            media = getattr(msg, msg.media.value)
            file_id = media.file_id
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
            
        filesarr = []
        for msg in msgs:
            channel_id = int(msg.get("channel_id"))
            msgid = msg.get("msg_id")
            info = await client.get_messages(channel_id, int(msgid))
            if info.media:
                file_type = info.media
                file = getattr(info, file_type.value)
                f_caption = getattr(info, 'caption', '')
                if f_caption:
                    f_caption = f_caption.html
                old_title = getattr(file, "file_name", "")
                title = formate_file_name(old_title)
                size=get_size(int(file.file_size))
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except:
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                if STREAM_MODE == True:
                    if info.video or info.document:
                        log_msg = info
                        fileName = {quote_plus(get_name(log_msg))}
                        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                        button = [[
                            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                        ],[
                            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                        ]]
                        reply_markup=InlineKeyboardMarkup(button)
                else:
                    reply_markup = None
                try:
                    msg = await info.copy(chat_id=message.from_user.id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    msg = await info.copy(chat_id=message.from_user.id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                except:
                    continue
            else:
                try:
                    msg = await info.copy(chat_id=message.from_user.id, protect_content=False)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    msg = await info.copy(chat_id=message.from_user.id, protect_content=False)
                except:
                    continue
            filesarr.append(msg)
            await asyncio.sleep(1) 
        await sts.delete()
        if AUTO_DELETE_MODE == True:
            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
            await asyncio.sleep(AUTO_DELETE_TIME)
            for x in filesarr:
                try:
                    await x.delete()
                except:
                    pass
            await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

    pre, decode_file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
    if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
        btn = [[
            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{username}?start="))
        ],[
            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
        ]]
        await message.reply_text(
            text="<b>You are not verified !\nKindly verify to continue !</b>",
            protect_content=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    try:
        msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
        if msg.media:
            media = getattr(msg, msg.media.value)
            title = formate_file_name(media.file_name)
            size=get_size(media.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            if STREAM_MODE == True:
                if msg.video or msg.document:
                    log_msg = msg
                    fileName = {quote_plus(get_name(log_msg))}
                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    button = [[
                        InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                        InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                    ],[
                        InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup=InlineKeyboardMarkup(button)
            else:
                reply_markup = None
            del_msg = await msg.copy(chat_id=message.from_user.id, caption=f_caption, reply_markup=reply_markup, protect_content=False)
        else:
            del_msg = await msg.copy(chat_id=message.from_user.id, protect_content=False)
        if AUTO_DELETE_MODE == True:
            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
            await asyncio.sleep(AUTO_DELETE_TIME)
            try:
                await del_msg.delete()
            except:
                pass
            await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
        return
    except:
        pass
        
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("<b>Shortener API updated successfully to</b> " + api)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = f"`/base_site (base_site)`\n\n<b>Current base site: None\n\n EX:</b> `/base_site shortnerdomain.com`\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if base_site == None:
            await update_user_info(user_id, {"base_site": base_site})
            return await m.reply("<b>Base Site updated successfully</b>")
            
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("<b>Base Site updated successfully</b>")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
        ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
        ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "clone":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CLONE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )          

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  



        
#----------------------------Post Code With Inlinebutton,Caption And Poster---------------------#

#----------------------------Post Code With Inlinebutton,Caption And Poster---------------------#

#poster make features developer - Ansh Vachhani

import re
import os
import logging
import base64
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from database.ia_filterdb import unpack_new_file_id
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

user_states = {}
CHANNELS = {
    "Channel 1": -1001842318978,
    "Channel 2": -1002308357802
}

CHANNELS = list(map(int, os.environ.get("CHANNELS", "-1001842318978 -1002308357802").split()))

print(CHANNELS)

async def delete_previous_reply(chat_id):
    """Deletes the previous bot message to keep the chat clean."""
    if chat_id in user_states and "last_reply" in user_states[chat_id]:
        try:
            await user_states[chat_id]["last_reply"].delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

@Client.on_message(filters.command("genpost") & filters.user(ADMINS))
async def genpost_command(client, message):
    """Handles the /genpost command."""
    try:
        reply = await message.reply("**Welcome to Rare Movie Post Feature!**\n\n"
                                    "👉🏻 Send the number of files you want to add.\n\n"
                                    "‼️ *Note:* Only enter a number.")
        user_states[message.chat.id] = {"state": "awaiting_num_files", "last_reply": reply}
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.private & (filters.text | filters.media) & ~filters.command("genpost"))
async def handle_message(client, message):
    """Handles user messages based on their current state."""
    try:
        chat_id = message.chat.id
        await delete_previous_reply(chat_id)

        if chat_id not in user_states:
            return
        
        state = user_states[chat_id]["state"]

        if state == "awaiting_num_files":
            try:
                num_files = int(message.text.strip())
                if num_files <= 0:
                    reply = await message.reply("⏩ Forward the file")
                    user_states[chat_id]["last_reply"] = reply
                    return

                user_states[chat_id].update({
                    "state": "awaiting_files",
                    "num_files": num_files,
                    "files_received": 0,
                    "file_ids": [],
                    "file_sizes": [],
                    "qualities": []
                })
                reply = await message.reply("**⏩ Forward the No: 1 file**")
                user_states[chat_id]["last_reply"] = reply

            except ValueError:
                await message.reply("Invalid input. Please enter a valid number.")

        elif state == "awaiting_files":
            if message.media:
                forwarded = await message.copy(chat_id=DIRECT_GEN_DB)
                file_id = str(forwarded.id)
                size = get_size(message.document.file_size) if message.document else "Unknown"

                quality_match = re.search(r"(480p|720p|1080p|HEVC|HDRip)", message.caption or "", re.IGNORECASE)
                quality = quality_match.group(1) if quality_match else None

                await message.delete()
                encoded_file_id = base64.urlsafe_b64encode(f"file_{file_id}".encode()).decode().strip("=")

                user_states[chat_id]["file_ids"].append(encoded_file_id)
                user_states[chat_id]["file_sizes"].append(size)
                user_states[chat_id]["qualities"].append(quality)
                user_states[chat_id]["files_received"] += 1

                if user_states[chat_id]["files_received"] < user_states[chat_id]["num_files"]:
                    reply = await message.reply(f"**⏩ Forward No: {user_states[chat_id]['files_received'] + 1} file(s)**")
                else:
                    reply = await message.reply("**Now send the movie name**\n\n"
                                                "**Example: Lover 2024 Hindi WEB-DL**")
                    user_states[chat_id]["state"] = "awaiting_title"

                user_states[chat_id]["last_reply"] = reply

        elif state == "awaiting_title":
            title = message.text.strip()
            cleaned_title = re.sub(r"[()\[\]{}:;'!]", "", title)
            imdb_data = await get_poster(cleaned_title)
            poster = imdb_data.get('poster') if imdb_data else None

            buttons = []
            for i, file_id in enumerate(user_states[chat_id]["file_ids"]):
                long_url = f"https://t.me/{temp.U_NAME}?start={file_id}"
                short_link_url = await short_link(long_url) or long_url

                quality = user_states[chat_id]['qualities'][i] or ""
                size = user_states[chat_id]['file_sizes'][i]
                label = f"{size} [ {quality} ]" if quality else size

                if i % 2 == 0:
                    buttons.append([InlineKeyboardButton(label, url=short_link_url)])
                else:
                    buttons[-1].append(InlineKeyboardButton(label, url=short_link_url))

            caption = (f"**🎬 {title} Tamil HDRip**\n\n"
                       "**[ 360p☆480p☆HEVC☆720p☆1080p ]✌**\n\n"
                       "**𓆩🔻𓆪 Direct Telegram Files 👇**\n\n"
                       "**✅ Note : [How to Download]({HOW_TO_POST_SHORT}) 👀**\n\n"
                       "**❤️‍🔥 Share with Friends ❤️‍🔥**")

            keyboard = InlineKeyboardMarkup(buttons)

            reply = await message.reply("**Select the target channel to post:**",
                                        reply_markup=InlineKeyboardMarkup(
                                            [[InlineKeyboardButton(name, callback_data=f"post_channel_{cid}")]
                                             for name, cid in CHANNELS.items()]
                                        ))

            user_states[chat_id].update({
                "state": "awaiting_channel_selection",
                "post_data": {"caption": caption, "poster": poster, "keyboard": keyboard}
            })
            user_states[chat_id]["last_reply"] = reply

@Client.on_callback_query(filters.regex(r"post_channel_(.+)"))
async def handle_channel_selection(client, callback_query):
    """Handles channel selection before posting."""
    chat_id = callback_query.message.chat.id
    if chat_id not in user_states or user_states[chat_id]["state"] != "awaiting_channel_selection":
        return
    
    selected_channel_id = int(callback_query.data.split("_")[-1])
    post_data = user_states[chat_id]["post_data"]

    try:
        if post_data["poster"]:
            await client.send_photo(selected_channel_id, post_data["poster"], caption=post_data["caption"],
                                    reply_markup=post_data["keyboard"])
        else:
            await client.send_message(selected_channel_id, post_data["caption"], reply_markup=post_data["keyboard"])
        
        await callback_query.message.edit("✅ **Post successfully sent!**")
    except Exception as e:
        await callback_query.message.edit(f"❌ **Failed to send post:** {e}")

    del user_states[chat_id]



        
#--------------------------Post Code with Caption And Poster-------------------------------#

#--------------------------Post Code with Caption And Poster-------------------------------#

@Client.on_message(filters.command("post") & filters.user(ADMINS))
async def post_command(client, message):
    try:
        await message.reply("**Wᴇʟᴄᴏᴍᴇ Tᴏ Usᴇ Oᴜʀ Rᴀʀᴇ Mᴏᴠɪᴇ Pᴏsᴛ Fᴇᴀᴛᴜʀᴇ:) Cᴏᴅᴇ ʙʏ [Rᴏxʏ ʟɪɴᴋᴢᴢ](https://t.me/PKlinkzz_admin_bot) 👨‍💻**\n\n**👉🏻Sᴇɴᴅ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ғɪʟᴇs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ👈🏻**\n\n**‼️ Nᴏᴛᴇ : Oɴʟʏ ɴᴜᴍʙᴇʀ**", disable_web_page_preview=True)
        user_states[message.chat.id] = {"state": "awaiting_num_files"}
    except Exception as e:
        await message.reply(f"Error occurred: {e}")



@Client.on_message(filters.private & (filters.text | filters.media) & ~filters.command("post"))
async def handle_message(client, message):
    try:
        chat_id = message.chat.id
        
        await delete_previous_reply(chat_id)
        
        if chat_id in user_states:
            current_state = user_states[chat_id]["state"]

            if current_state == "awaiting_num_files":
                try:
                    num_files = int(message.text.strip())

                    if num_files <= 0:
                        rply = await message.reply("⏩ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ")
                        user_states[chat_id]["last_reply"] = rply
                        return

                    user_states[chat_id] = {
                        "state": "awaiting_files",
                        "num_files": num_files,
                        "files_received": 0,
                        "file_ids": [],
                        "file_sizes": [],
                        "stream_links": []
                    }

                    reply_message = await message.reply("**⏩ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ɴᴏ: 1 ғɪʟᴇ**")
                    user_states[chat_id]["last_reply"] = reply_message
                        
                except ValueError:
                    await message.reply("Invalid input. Please enter a valid number.")

            elif current_state == "awaiting_files":
                if message.media:
                    file_type = message.media
                    forwarded_message = await message.copy(chat_id=DIRECT_GEN_DB)
                    file_id = str(forwarded_message.id)  # Ensure correct file ID extraction
            
                    log_msg = await message.copy(chat_id=DIRECT_GEN_DB)
                    stream_link = await gen_link(log_msg)
            
                    size = get_size(getattr(message, file_type.value).file_size)
                    await message.delete()
                else:
                    forwarded_message = await message.forward(chat_id=DIRECT_GEN_DB)
                    file_id = str(forwarded_message.id)
            
                # ✅ Correctly encode file ID
                string = f"file_{file_id}"
                encoded_file_id = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
            
                # Save file data
                user_states[chat_id]["file_ids"].append(encoded_file_id)  # Store encoded ID
                user_states[chat_id]["file_sizes"].append(size)
                user_states[chat_id]["stream_links"].append(stream_link)
            
                user_states[chat_id]["files_received"] += 1
                files_received = user_states[chat_id]["files_received"]
                num_files_left = user_states[chat_id]["num_files"] - files_received
            
                if num_files_left > 0:
                    reply_message = await message.reply(f"**⏩ Forward the No: {files_received + 1} File(s)**")
                    user_states[chat_id]["last_reply"] = reply_message                     
                else:
                    reply_message = await message.reply("**Now send the movie name**\n\n**Example: Lover 2024 Hindi WEB-DL**")                    
                    user_states[chat_id]["state"] = "awaiting_title"
                    user_states[chat_id]["last_reply"] = reply_message
            
            elif current_state == "awaiting_title":
                title = message.text.strip()
                title_clean = re.sub(r"[()\[\]{}:;'!]", "", title)
                cleaned_title = clean_title(title_clean)
            
                imdb_data = await get_poster(cleaned_title)
                poster = imdb_data.get('poster') if imdb_data else None
            
                file_info = []
                for i, file_id in enumerate(user_states[chat_id]["file_ids"]):
                    long_url = f"https://t.me/{temp.U_NAME}?start={file_id}"  # ✅ Use correctly encoded ID
                    short_link_url = await short_link(long_url) or long_url  # ✅ Fallback to long URL
                    file_info.append(f"》{user_states[chat_id]['file_sizes'][i]} : {short_link_url}")
            
                file_info_text = "\n\n".join(file_info)
            
                stream_links_info = []
                for i, stream_link in enumerate(user_states[chat_id]["stream_links"]):
                    if isinstance(stream_link, tuple):  # ✅ Fix duplicate link issue
                        stream_link = stream_link[0]  # Pick only one valid URL
                    short_stream_link_url = await short_link(stream_link) or stream_link
                    stream_links_info.append(f"》{user_states[chat_id]['file_sizes'][i]} : {short_stream_link_url}")
                
                stream_links_text = "\n\n".join(stream_links_info)                
                summary_message = f"**🎬{title} Tamil HDRip**\n\n**[ 𝟹𝟼𝟶ᴘ☆𝟺𝟾𝟶ᴘ☆Hᴇᴠᴄ☆𝟽𝟸𝟶ᴘ☆𝟷𝟶𝟾𝟶ᴘ ]✌**\n\n**𓆩🔻𓆪 Dɪʀᴇᴄᴛ Tᴇʟᴇɢʀᴀᴍ Fɪʟᴇs Oɴʟʏ👇**\n\n**{file_info_text}**\n\n**✅ Note : [Hᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ]({HOW_TO_POST_SHORT})👀**\n\n**𓆩🔻𓆪 Sᴛʀᴇᴀᴍ/Fᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ 👇**\n\n**{stream_links_text}**\n\n**✅ Note : [Hᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ]({HOW_TO_POST_SHORT})👀**\n\n**Mᴏᴠɪᴇ Gʀᴏᴜᴘ 𝟸𝟺/𝟽 : @Roxy_Request_24_7**\n\n**❤️‍🔥ー𖤍 𓆩 sʜᴀʀᴇ ᴡɪᴛʜ ғʀɪᴇɴᴅs 𓆪 𖤍ー❤️‍🔥**"
                summary_messages = f"{title_clean}, {cleaned_title}"
                if poster:
                    await message.reply_photo(poster, caption=summary_message)
                else:
                    await message.reply(summary_messages)
                    
                await message.delete()
                del user_states[chat_id]

        else:
            return
    except Exception as e:
        await message.reply(f"Error occurred: {e}") 
