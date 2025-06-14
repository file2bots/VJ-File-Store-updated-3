# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import logging
import random
import asyncio
import re
import json
import base64
import math
from urllib.parse import quote_plus

from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info, get_short_link
from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant, InviteRequestSent
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.types import *


# Lazy import to prevent circular dependency
from config import *
from utils import get_poster

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
STEP_STORE = {}

#--------------------------force sub code--------------------------#
async def get_invite_link(bot, chat_id):
    """Get an invite link for a channel (username or export link)."""
    try:
        chat = await bot.get_chat(chat_id)
        if chat.username:
            return f"https://t.me/{chat.username}"
        else:
            return await bot.export_chat_invite_link(chat_id)
    except ChatAdminRequired:
        logger.warning(f"Bot is not admin in the channel: {chat_id}")
    except Exception as e:
        logger.error(f"Failed to get invite link for {chat_id}: {e}")
    return None

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
#--------------------------force sub code--------------------------#
def get_size(size):
    """Get size in a readable format:
       - Round up to a whole number for MB and below
       - Round up to 1 decimal place for GB and above
    """

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    
    while size >= 1024.0 and i < len(units) - 1:
        i += 1
        size /= 1024.0

    if units[i] in ["GB", "TB", "PB", "EB"]:
        return "%.1f%s" % (math.ceil(size * 10) / 10, units[i])  # Round up to 1 decimal place
    else:
        return "%d%s" % (math.ceil(size), units[i])  # Round up to whole number
        
def formate_file_name(file_name):
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    user_id = message.from_user.id
    mention = message.from_user.mention
    username = (await client.get_me()).username

    # Ensure AUTH_CHANNEL is a list
    auth_channels = [AUTH_CHANNEL] if isinstance(AUTH_CHANNEL, (str, int)) else AUTH_CHANNEL

    # ✅ Force Subscription Check
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if message.command[1]:
                    btn.append([InlineKeyboardButton("♻️ Tʀʏ ᴀɢᴀɪɴ ♻️", url=f"https://t.me/{username}?start={message.command[1]}")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Tʀʏ ᴀɢᴀɪɴ ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(text=f"<b>👋 Hᴇʟʟᴏ {message.from_user.mention},\n\n➤ Yᴏᴜ ᴡɪʟʟ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ.\n\n➤ Fɪʀsᴛ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 𝐉ᴏɪɴ ᴜᴘᴅᴀᴛᴇ 𝐂ʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ, ᴛʜᴇɴ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 𝐑ᴇᴏ̨ᴜᴇ𝐬ᴛ ᴛᴏ 𝐉ᴏɪɴ ʙᴜᴛᴛᴏɴ.\n\n➤ Aғᴛᴇʀ ᴛʜᴀᴛ, ᴛʀʏ ᴀᴄᴄᴇssɪɴɢ ᴛʜᴀᴛ ᴍᴏᴠɪᴇ ᴛʜᴇɴ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 𝐓ʀʏ 𝐀ɢᴀɪɴ ʙᴜᴛᴛᴏɴ.</b>", reply_markup=InlineKeyboardMarkup(btn))
                return
        except Exception as e:
            print(e)
            
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

#---------------------------------Link and Batch------------------------------------------#
async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False     

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
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        

@Client.on_message(filters.command("batch") & filters.create(lambda _, __, m: True))  # put your 'allowed' filter here
async def handle_batch(bot, message):
    user_id = message.from_user.id
    username = (await bot.get_me()).username

    # Validate input links
    parts = message.text.strip().split()
    if len(parts) != 3:
        return await message.reply(
            "Use correct format:\n/batch <first_link> <last_link>\nExample:\n/batch https://t.me/channel/100 https://t.me/channel/110"
        )

    _, first_link, last_link = parts
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    match = regex.match(first_link)
    if not match:
        return await message.reply("Invalid first link.")
    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int("-100" + f_chat_id)

    match = regex.match(last_link)
    if not match:
        return await message.reply("Invalid last link.")
    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int("-100" + l_chat_id)

    if f_chat_id != l_chat_id:
        return await message.reply("Both links must be from the same chat.")

    # Check access to chat
    try:
        await bot.get_chat(f_chat_id)
    except ChannelInvalid:
        return await message.reply("I don't have access to that channel/group. Make me admin or check privacy.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid chat link.")
    except Exception as e:
        return await message.reply(f"Error accessing chat: {e}")

    status_msg = await message.reply("🔍 Fetching messages...")

    files = []
    poster_file_id = None
    imdb_caption_list = []
    total_files = 0

    # Iterate messages in range (l_msg_id to f_msg_id because iter_messages works backward)
    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        if msg.empty or msg.service:
            continue
        total_files += 1
        files.append({"channel_id": f_chat_id, "msg_id": msg.id})

        # Get poster only from first valid file
        if not poster_file_id:
            file_name = None
            if msg.video:
                file_name = msg.video.file_name
            elif msg.document:
                file_name = msg.document.file_name
            if file_name:
                imdb = await get_poster(file_name)
                if imdb and imdb.get("poster_url"):
                    try:
                        # Download poster image temporarily and send to get file_id
                        photo_path = await bot.download_media(imdb["poster_url"])
                        sent = await bot.send_photo(message.chat.id, photo_path, caption="Poster fetched. Processing...")
                        poster_file_id = sent.photo.file_id
                        await sent.delete()
                        os.remove(photo_path)
                    except Exception:
                        pass
                imdb_caption_list.append(f'{imdb.get("title", "Unknown")} ⭐ {imdb.get("rating", "N/A")}')
        else:
            imdb_caption_list.append("")  # keep index same

    if not files:
        return await status_msg.edit("No valid files found in the specified range.")

    # Save files list JSON
    json_filename = f"batch_{user_id}.json"
    with open(json_filename, "w") as f:
        json.dump(files, f)

    # Upload batch JSON to log channel
    post = await bot.send_document(LOG_CHANNEL, json_filename, file_name="Batch.json", caption="Batch File for Filestore")
    os.remove(json_filename)

    batch_id_encoded = base64.urlsafe_b64encode(str(post.id).encode()).decode().strip("=")
    if WEBSITE_URL_MODE:
        batch_link = f"{WEBSITE_URL}?start=BATCH-{batch_id_encoded}"
    else:
        batch_link = f"https://t.me/{username}?start=BATCH-{batch_id_encoded}"

    # Save in STEP_STORE to wait for title input
    STEP_STORE[user_id] = {
        "poster_file_id": poster_file_id,
        "imdb_captions": imdb_caption_list,
        "batch_link": batch_link,
        "total_files": total_files,
    }

    await status_msg.edit(
        "✅ Batch files collected and poster fetched (if available).\n"
        "Now, please send me the *title* you want to use for this batch."
    )


@Client.on_message(filters.text & filters.private)
async def receive_title(bot, message):
    user_id = message.from_user.id
    if user_id not in STEP_STORE:
        return  # Not waiting for batch title

    data = STEP_STORE.pop(user_id)
    title = message.text.strip()
    poster_file_id = data.get("poster_file_id")
    imdb_captions = data.get("imdb_captions", [])
    batch_link = data.get("batch_link")
    total_files = data.get("total_files")

    # Build caption
    caption = f"<b>🎬 {title}</b>\n\n"
    caption += f"<b>Total Files:</b> <code>{total_files}</code>\n\n"

    # Add first 20 imdb captions if available
    caption_lines = [f"{i+1}. {cap}" for i, cap in enumerate(imdb_captions) if cap]
    if caption_lines:
        caption += "\n".join(caption_lines[:20]) + "\n\n"

    caption += f"🔗 <b>Batch Link:</b> {batch_link}"

    # Send poster with caption if poster exists, else send text only
    if poster_file_id:
        await bot.send_photo(message.chat.id, poster_file_id, caption=caption)
    else:
        await message.reply(caption)
        

        
#----------------------------Post Code With Inlinebutton,Caption And Poster---------------------#

import re
import logging
import base64
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from database.ia_filterdb import unpack_new_file_id
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram import Client, filters
from pyrogram.types import Message

user_states = {}

async def delete_previous_reply(chat_id):
    """Deletes the last reply message sent by the bot."""
    if chat_id in user_states and "last_reply" in user_states[chat_id]:
        try:
            await user_states[chat_id]["last_reply"].delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

@Client.on_message(filters.command("post") & filters.user(ADMINS))
async def post_command(client, message):
    """Starts the movie posting process."""
    try:
        await message.reply("**Welcome to the Rare Movie Post Feature!**\n\n"
                            "👉🏻 Send the number of files you want to add.\n\n"
                            "‼️ *Note:* Only enter a number.", disable_web_page_preview=True)
        user_states[message.chat.id] = {"state": "awaiting_num_files"}
    except Exception as e:
        await message.reply(f"Error occurred: {e}")

@Client.on_message(filters.private & (filters.text | filters.media) & ~filters.command("post"))
async def handle_message(client, message):
    """Handles user messages during the posting process."""
    try:
        chat_id = message.chat.id
        await delete_previous_reply(chat_id)
        
        if chat_id in user_states:
            current_state = user_states[chat_id]["state"]

            if current_state == "awaiting_num_files":
                try:
                    num_files = int(message.text.strip())

                    if num_files <= 0:
                        rply = await message.reply("⏩ Forward the file")
                        user_states[chat_id]["last_reply"] = rply
                        return

                    user_states[chat_id] = {
                        "state": "awaiting_files",
                        "num_files": num_files,
                        "files_received": 0,
                        "file_ids": [],
                        "file_sizes": [],
                        "qualities": []
                    }

                    reply_message = await message.reply("**⏩ Forward the No: 1 file**")
                    user_states[chat_id]["last_reply"] = reply_message
                        
                except ValueError:
                    await message.reply("Invalid input. Please enter a valid number.")

            elif current_state == "awaiting_files":
                if message.media:
                    forwarded_message = await message.copy(chat_id=DIRECT_GEN_DB)
                    file_id = str(forwarded_message.id)

                    size = get_size(message.document.file_size) if message.document else "Unknown"
                    quality_match = re.search(r"(480p|720p|1080p|HEVC|4K)", message.caption or "", re.IGNORECASE)
                    quality = quality_match.group(1) if quality_match else None

                    await message.delete()

                    encoded_file_id = base64.urlsafe_b64encode(f"file_{file_id}".encode("ascii")).decode().strip("=")
                    user_states[chat_id]["file_ids"].append(encoded_file_id)
                    user_states[chat_id]["file_sizes"].append(size)
                    user_states[chat_id]["qualities"].append(quality)

                    user_states[chat_id]["files_received"] += 1
                    files_received = user_states[chat_id]["files_received"]
                    num_files_left = user_states[chat_id]["num_files"] - files_received

                    if num_files_left > 0:
                        reply_message = await message.reply(f"**⏩ Forward the No: {files_received + 1} File(s)**")
                        user_states[chat_id]["last_reply"] = reply_message                     
                    else:
                        reply_message = await message.reply("**Now send the movie name**\n\n"
                                                            "**Example: Lover 2024 Hindi WEB-DL**")                    
                        user_states[chat_id]["state"] = "awaiting_title"
                        user_states[chat_id]["last_reply"] = reply_message
            
            elif current_state == "awaiting_title":
                title = message.text.strip()
                title_clean = re.sub(r"[()\[\]{}:;'!]", "", title)
                cleaned_title = clean_title(title_clean)
            
                imdb_data = await get_poster(cleaned_title)
                poster = imdb_data.get('poster') if imdb_data else None
            
                # Creating formatted text-based links with bold
                caption = (
                    f"🎬 <b>{title} Tamil HDRip</b>\n\n"
                    "📀 <b>❤️‍🔥 ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ - <a href='https://t.me/Tamilmobx'>@Tamilmobx</a></b>\n\n"
                    "<b>⚡ ᴅɪʀᴇᴄᴛ ғɪʟᴇs / ꜰᴀꜱᴛ ʟɪɴᴋ 🚀</b>\n\n"
                )

                for i, file_id in enumerate(user_states[chat_id]["file_ids"]):
                    if WEBSITE_URL_MODE == True:
                        long_url = f"{WEBSITE_URL}?start={file_id}"
                    else:
                        long_url = f"https://t.me/{temp.U_NAME}?start={file_id}"
                    short_link_url = await short_link(long_url) or long_url

                    quality = user_states[chat_id]['qualities'][i] or "Unknown"
                    size = user_states[chat_id]['file_sizes'][i]
                    
                    #caption += f"🗳 **{size} [{quality}]** - [**Generated Link**]({short_link_url})\n"
                    #caption += f"🗳 **{size} {quality}** - [**Generated Link**]({short_link_url})\n"
                    caption += f"🗳 <b>{size} [{quality}] ➜ <a href='{short_link_url}'>📥 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗</a></b>\n\n"

                caption += (
                    "<b>🛠 Dᴏᴡɴʟᴏᴀᴅ Gᴜɪᴅᴇ : <a href='https://t.me/Howtodowloa/9'>📖 Cʟɪᴄᴋ Hᴇʀᴇ 𓆪</a> 👀</b>\n\n"
                    "<b>🍿 𓆩 Mᴏᴠɪᴇ Rᴇǫ 𝟸𝟺x𝟽 ☛ : <a href='https://t.me/+6QFNHZzurnFjY2Jl'>📢 Cʟɪᴄᴋ Hᴇʀᴇ</a> 🔥</b>\n\n"
                    "<b>ー♡꘎ 𓆩 Sʜᴀʀᴇ Wɪᴛʜ Fʀɪᴇɴᴅs 𓆪꘎♡ー</b>"
                )

                if poster:
                    await message.reply_photo(poster, caption=caption)
                else:
                    await message.reply(caption)
                    
                await message.delete()
                del user_states[chat_id]

        else:
            return
    except Exception as e:
        await message.reply(f"Error occurred: {e}")
