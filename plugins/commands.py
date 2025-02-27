import re
import os
import io
import logging
import random
import asyncio
from validators import domain
from shortzy import Shortzy
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import *
from utils import get_message_id
from utils import verify_user, check_token, check_verification, get_token
from config import *
import json
import base64
import requests
from telethon.tl import types
from utils import humanbytes
from urllib.parse import quote_plus
from plugins.dbusers import Database
from asyncio import TimeoutError
from CloudXbotz.utils.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)

db = Database(DB_URI, DB_NAME)
CMD = ["/", "."]
from imdb import IMDb
from io import BytesIO
from PIL import Image
imdb = IMDb()
from imdb._exceptions import IMDbDataAccessError
#--------------------------------

BATCH_FILES = {}
async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            pass
    return btn

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
    file_name = '@TamilMob_Zone - ' + ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if message.command[1]:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start={message.command[1]}")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on try again button. 😇</b>", reply_markup=InlineKeyboardMarkup(btn))
                return
        except Exception as e:
            print(e)
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [
            [
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ', url='https://t.me/CloudxAdmin_Bot'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/+mDKrpo2FcD04Nzll')
            ],
            [
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
            ],
            [
            InlineKeyboardButton('✇ Jᴏɪɴ Mᴏᴠɪᴇs Cʜᴀɴɴᴇʟ ✇', callback_data='extra')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        me = await client.get_me()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, me.mention),
            reply_markup=reply_markup
        )
        return
    
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

    elif query.data == "start":
        buttons = [
            [
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ', url='https://t.me/CloudxAdmin_Bot'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/+mDKrpo2FcD04Nzll')
            ],
            [
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
            ],
            [
            InlineKeyboardButton('✇ Jᴏɪɴ Mᴏᴠɪᴇs Cʜᴀɴɴᴇʟ ✇', callback_data='extra')
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
    
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('🍿 Uᴘᴅᴀᴛᴇᴅ Cʜᴀɴɴᴇʟs 📌', url='https://t.me/+88LpGR0t8_1lNzU1')
        ],[
            InlineKeyboardButton('🔎 ᴍᴏᴠɪᴇ sᴇᴀʀᴄʜ ʙᴏᴛ 🔍', url='https://t.me/SimplySearchBot')
        ],[
            InlineKeyboardButton('🔞 Rᴇsᴛʀɪᴄᴛᴇᴅ Aʀᴇᴀ 🔞', url='https://t.me/+UiiWHjVno04yMjU1')
        ],[
            InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start'),
            InlineKeyboardButton('Cʟᴏsᴇ🔒', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.JOINUPDATES_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
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


#--------------------------------SHORTENER------------------------------------------------#

async def get_shortlink(link):
    url = 'https://modijiurl.com/api'
    params = {'api': SHORTENER_API, 'url': link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
            data = await response.json()
            return data["shortenedUrl"]


#--------------------------------SHORTENER------------------------------------------------#


#----------------------------------POST------------------------------------------------------#





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
    
    direct_telegram_links = []
    stream_links = []
    online_links = []

    for i, (media, msg_id, forward_message, post_message_id) in enumerate(media_list):
        string = f"get-{msg_id * abs(CHANNEL_ID)}"
        base64_string = await encode(string)
        file_size = humanbytes(media.file_size) if media.file_size else ""
        linkk = await get_shortlink(f"{RXL}/{base64_string}")
        link = f"<b>{file_size} :</b> {linkk}\n"
        direct_telegram_links.append(link)
        direct_telegram_lines = '\n'.join(direct_telegram_links)

    # Construct unique stream links for each file
        online_linkk = await get_shortlink(f"{URL}{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  # Using post_message_id
        stream_linkk = await get_shortlink(f"{URL}watch/{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  # Using post_message_id
        stream_link = f"<b>{file_size} :</b> {stream_linkk}\n"
        online_link = f"<b>{file_size} :</b> {online_linkk}\n"
        stream_links.append(stream_link)
        online_links.append(online_link)
        stream_lines = '\n'.join(stream_links)
        online_lines = '\n'.join(online_links)

# Join all links outside the loop after constructing all links


    

    imdb_info = await get_poster(extract_movie_name(filename))
    
    # Check if IMDb info is found
    if imdb_info:
        # Download the IMDb poster image
        imdb_image_response = requests.get(imdb_info['poster'])
        imdb_image_data = io.BytesIO(imdb_image_response.content)
    else:
        # Use a default image if IMDb info is not found
        # Replace 'common_image_url' with the URL of the common image you want to use
        common_image_url = 'https://telegra.ph/file/74707bb075903640ed3f6.jpg'
        imdb_image_data = io.BytesIO(requests.get(common_image_url).content)
    # Send the IMDb poster image as a photo along with other details
    await client.send_photo(
        chat_id=message.chat.id,
        photo=imdb_image_data,
        caption=f'<b>🎬 {filename}\n\n'
                f'✅ Note : [ <a href=https://t.me/tnlinkdown/9>How to download</a> ]\n\n'
                f'🔻 Direct Telegram Files 🔻\n\n{direct_telegram_lines}\n'
                f'🔻 Stream / Fast Download 🔻\n\n{stream_lines}\n'
                f'@RX_LinkZz || @RolexMoviesOXO\n\n'
                f'Share and Support Us 🫶🏻</b>'
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
    return match.group(1) if match else filename#--------------------------------SHORTENER------------------------------------------------#

async def get_shortlink(link):
    url = 'https://modijiurl.com/api'
    params = {'api': SHORTENER_API, 'url': link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
            data = await response.json()
            return data["shortenedUrl"]


#--------------------------------SHORTENER------------------------------------------------#


#----------------------------------POST------------------------------------------------------#





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
    
    direct_telegram_links = []
    stream_links = []
    online_links = []

    for i, (media, msg_id, forward_message, post_message_id) in enumerate(media_list):
        string = f"get-{msg_id * abs(CHANNEL_ID)}"
        base64_string = await encode(string)
        file_size = humanbytes(media.file_size) if media.file_size else ""
        linkk = await get_shortlink(f"{RXL}/{base64_string}")
        link = f"<b>{file_size} :</b> {linkk}\n"
        direct_telegram_links.append(link)
        direct_telegram_lines = '\n'.join(direct_telegram_links)

    # Construct unique stream links for each file
        online_linkk = await get_shortlink(f"{URL}{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  # Using post_message_id
        stream_linkk = await get_shortlink(f"{URL}watch/{str(post_message_id)}/{quote_plus(get_name(forward_message))}?hash={get_hash(forward_message)}")  # Using post_message_id
        stream_link = f"<b>{file_size} :</b> {stream_linkk}\n"
        online_link = f"<b>{file_size} :</b> {online_linkk}\n"
        stream_links.append(stream_link)
        online_links.append(online_link)
        stream_lines = '\n'.join(stream_links)
        online_lines = '\n'.join(online_links)

# Join all links outside the loop after constructing all links


    

    imdb_info = await get_poster(extract_movie_name(filename))
    
    # Check if IMDb info is found
    if imdb_info:
        # Download the IMDb poster image
        imdb_image_response = requests.get(imdb_info['poster'])
        imdb_image_data = io.BytesIO(imdb_image_response.content)
    else:
        # Use a default image if IMDb info is not found
        # Replace 'common_image_url' with the URL of the common image you want to use
        common_image_url = 'https://telegra.ph/file/74707bb075903640ed3f6.jpg'
        imdb_image_data = io.BytesIO(requests.get(common_image_url).content)
    # Send the IMDb poster image as a photo along with other details
    await client.send_photo(
        chat_id=message.chat.id,
        photo=imdb_image_data,
        caption=f'<b>🎬 {filename}\n\n'
                f'✅ Note : [ <a href=https://t.me/tnlinkdown/9>How to download</a> ]\n\n'
                f'🔻 Direct Telegram Files 🔻\n\n{direct_telegram_lines}\n'
                f'🔻 Stream / Fast Download 🔻\n\n{stream_lines}\n'
                f'@RX_LinkZz || @RolexMoviesOXO\n\n'
                f'Share and Support Us 🫶🏻</b>'
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
