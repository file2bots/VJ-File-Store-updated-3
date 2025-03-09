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
from plugins.dbusers import *
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant, InviteRequestSent, PeerIdInvalid
from pyrogram.types import *

from shortzy import Shortzy #
from CloudXbotz.bot import StreamBot #

# Lazy import to prevent circular dependency
from config import *

# Import utils functions separately to avoid circular import
from utils import (
    verify_user, check_token, check_verification, get_token, get_size,
    gen_link, clean_title, get_poster, temp, short_link
)

# Import TechVJ utilities safely
from CloudXbotz.utils.file_properties import get_name, get_hash, get_media_file_size
from CloudXbotz.utils.human_readable import humanbytes #
from Script import script #

# Initialize logger
logger = logging.getLogger(__name__)

# Database
#db = Database(Var.DATABASE_URL, Var.name)

# Temporary Storage
class Temp:
    U_NAME = None
    B_NAME = None

BATCH_FILES = {}

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
#-------------------------------------------------------------------------------------
@StreamBot.on_message(filters.command("Set") & filters.private)
async def set_handler(client, message):
    await db.hs_add_user(client, message)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💖 Bot Owner", url="https://t.me/Heart_Thieft")],
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/TamizhFiles/51"),
            InlineKeyboardButton("🎬 Movies", url="https://t.me/+hZG8OILc-qA3MzFl")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ])

    await message.reply_text(
        text=script.START_TXT.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )



  



        

#---------------------------SETTINGS CALLBACK CODE-----------------------------#
# ⚙️ Settings Menu
@StreamBot.on_callback_query(filters.regex("^settings_menu$"))
async def settings_menu(client, query):
    """Displays the main settings menu."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Shortener Settings", callback_data="shortener_settings")],
        [InlineKeyboardButton("📝 Caption Settings", callback_data="caption_settings")],
        [InlineKeyboardButton("📢 Channel Settings", callback_data="channel_settings")],  # ✅ New Button
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

    new_text = "⚙️ **Settings Panel**\n\nCustomize your bot preferences:"

    try:
        await query.message.edit_text(new_text, reply_markup=keyboard)
    except Exception as e:
        logger.exception(e)
        await query.answer("You are already in the Settings Panel.", show_alert=True)




#--------------------------------------- Shortner Settings --------------------------------------#


@StreamBot.on_callback_query(filters.regex("^shortener_settings$"))
async def show_shortener_settings(client, query: CallbackQuery):
    """Displays the shortener settings menu with toggle, view, set, and remove options."""
    user_id = query.from_user.id
    user_data = await db.get_user(user_id) or {}

    shortener_api = user_data.get("shortener_api", "❌ Not Set")
    shortener_url = user_data.get("shortener_url", "❌ Not Set")
    shortener_status = "✅ Enabled" if user_data.get("shortener_enabled", False) else "❌ Disabled"

    new_text = (
        f"⚙️ **Shortener Settings**\n\n"
        f"🔗 **Status:** {shortener_status}\n"
        f"🔑 **API:** `{shortener_api}`\n"
        f"🌐 **URL:** `{shortener_url}`\n\n"
        "Manage your link shortener preferences below."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔗 Shortener: {shortener_status}", callback_data="toggle_shortener")],
        [InlineKeyboardButton("🔑 Set API", callback_data="set_shortener_api"),
         InlineKeyboardButton("👁 View API", callback_data="view_shortener_api")],
        [InlineKeyboardButton("🌐 Set URL", callback_data="set_shortener_url"),
         InlineKeyboardButton("👁 View URL", callback_data="view_shortener_url")],
        [InlineKeyboardButton("❌ Remove API", callback_data="remove_shortener_api"),
         InlineKeyboardButton("❌ Remove URL", callback_data="remove_shortener_url")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
    ])

    if query.message.text != new_text:
        await query.message.edit_text(new_text, reply_markup=keyboard)

#--------------------------------------- Caption Settings --------------------------------------#

# 📝 Caption Settings
@StreamBot.on_callback_query(filters.regex("^caption_settings$"))
async def caption_settings(client, query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
         InlineKeyboardButton("📜 View Caption", callback_data="view_caption")],
        [InlineKeyboardButton("🗑 Delete Caption", callback_data="del_caption")],
        [InlineKeyboardButton("📖 Caption Guide", callback_data="caption_guide")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
    ])
    await query.message.edit_text("📝 **Caption Settings**\n\nManage your caption preferences:", reply_markup=keyboard)

#--------------------------------------- Channel Settings --------------------------------------#


#--------------------------------------- 🛠 Shortener Enable/Disable Feature --------------------------------------#

@StreamBot.on_callback_query(filters.regex("^toggle_shortener$"))
async def toggle_shortener(client, query: CallbackQuery):
    """Enables or disables the shortener for a user."""
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)

    # Toggle shortener status
    shortener_enabled = not user_data.get("shortener_enabled", False)
    await db.update_user_info(user_id, {"shortener_enabled": shortener_enabled})  

    # Confirmation message
    status = "✅ Enabled" if shortener_enabled else "❌ Disabled"
    await query.answer(f"Shortener is now {status}", show_alert=True)

    # Refresh settings menu
    await show_shortener_settings(client, query)

#--------------------------------------- Forwarded Message & Save Channel ID --------------------------------------#


    
#--------------------------------------- Caption Guides --------------------------------------#

@StreamBot.on_callback_query(filters.regex("^stats$"))
async def bot_stats(client, query):
    """Displays bot statistics including total users, total links, and user-specific stats."""
    
    total_users = await db.get_total_users()  # Get total users from DB
    total_links = await db.get_total_links()  # Get total links stored
    user_links = await db.get_user_links(query.from_user.id)  # Get specific user links count
    
    stats_text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 **Total Users**: `{total_users}`\n"
        f"🔗 **Total Links Processed**: `{total_links}`\n"
        f"📌 **Your Processed Links**: `{user_links}`\n\n"
        "🔄 Data updates in real-time."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
    ])

    await query.message.edit_text(stats_text, reply_markup=keyboard)

#--------------------------------------- Caption Guides --------------------------------------#

# 📖 Caption Guide
@StreamBot.on_callback_query(filters.regex("^caption_guide$"))
async def caption_guide(client, query: CallbackQuery):
    guide_text = """
📖 **Caption Guide**

**Example Format:**  

`🎬 {file_name}  

📦 File Size : {file_size}  

🗳 Fast Stream 🚀 : {watch_link}  

🚀 Fast Download 🗳 : {download_link}  

〽️ Powered by @HeartxBotz`

---

**Available Placeholders:**  
- `{file_name}` → File name  
- `{previouscaption}` → Previous caption  
- `{file_size}` → File size  
- `{watch_link}` → Streaming link  
- `{download_link}` → Download link  
    """
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="caption_settings")]])
    await query.message.edit_text(guide_text, reply_markup=keyboard)
    
#--------------------------------------- Set Command Codes --------------------------------------#

# 🔗 Set Shortener API
@StreamBot.on_callback_query(filters.regex("^set_shortener_api$"))
async def set_shortener_api(client, query: CallbackQuery):
    await db.update_user_info(query.from_user.id, {"awaiting": "shortener_api"})
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="shortener_settings")]])
    await query.message.edit_text("📌 Send your Shortener API key now!", reply_markup=keyboard)

# 🔗 Set Shortener URL
@StreamBot.on_callback_query(filters.regex("^set_shortener_url$"))
async def set_shortener_url(client, query: CallbackQuery):
    await db.update_user_info(query.from_user.id, {"awaiting": "shortener_url"})
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="shortener_settings")]])
    await query.message.edit_text("📌 Send your Shortener URL now!", reply_markup=keyboard)

# 📝 Set Caption
@StreamBot.on_callback_query(filters.regex("^set_caption$"))
async def set_caption(client, query: CallbackQuery):
    await db.update_user_info(query.from_user.id, {"awaiting": "caption"})
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="caption_settings")]])
    await query.message.edit_text("📌 Send your custom caption now!", reply_markup=keyboard)


#------------------------------------------- View Codes --------------------------------------#

"""# 📜 View Shortener API
@StreamBot.on_callback_query(filters.regex("^view_shortener_api$"))
async def view_shortener_api(client, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    api_key = user_data.get("shortener_api", "❌ Not Set")
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="shortener_settings")]])
    await query.message.edit_text(f"🔑 **Your Shortener API Key:**\n\n`{api_key}`", reply_markup=keyboard)

# 📜 View Shortener URL
@StreamBot.on_callback_query(filters.regex("^view_shortener_url$"))
async def view_shortener_url(client, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    url = user_data.get("shortener_url", "❌ Not Set")

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="shortener_settings")]])
    await query.message.edit_text(f"🌍 **Your Shortener URL:**\n\n`{url}`", reply_markup=keyboard)

# 📜 View Caption
@StreamBot.on_callback_query(filters.regex("^view_caption$"))
async def view_caption(client, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await db.get_user(user_id)
    caption = user_data.get("caption", "❌ Not Set")

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="caption_settings")]])
    await query.message.edit_text(f"📝 **Your Caption:**\n\n`{caption}`", reply_markup=keyboard)
"""

#--------------------------------------- Pop-Up View Codes --------------------------------------#

# 📜 View Shortener API (Popup)
@StreamBot.on_callback_query(filters.regex("^view_shortener_api$"))
async def view_shortener_api(client, query: CallbackQuery):
    api_key = await db.get_shortener_api(query.from_user.id)
    await query.answer(f"🔑 Shortener API:\n{api_key}", show_alert=True)

# 📜 View Shortener URL (Popup)
@StreamBot.on_callback_query(filters.regex("^view_shortener_url$"))
async def view_shortener_url(client, query: CallbackQuery):
    url = await db.get_shortener_url(query.from_user.id)
    await query.answer(f"🔗 Shortener URL:\n{url}", show_alert=True)

# 📜 View Caption (Popup)
@StreamBot.on_callback_query(filters.regex("^view_caption$"))
async def view_caption(client, query: CallbackQuery):
    caption = await db.get_caption(query.from_user.id)
    await query.answer(f"📝 Caption:\n{caption}", show_alert=True)



#--------------------------------------- 🗑 Remove (Popup Alert) --------------------------------------#

# 🗑 Remove Shortener API (Popup)
@StreamBot.on_callback_query(filters.regex("^remove_shortener_api$"))
async def remove_shortener_api(client, query: CallbackQuery):
    await db.remove_shortener_api(query.from_user.id)
    await query.answer("🗑 Shortener API removed successfully!", show_alert=True)

# 🗑 Remove Shortener URL (Popup)
@StreamBot.on_callback_query(filters.regex("^remove_shortener_url$"))
async def remove_shortener_url(client, query: CallbackQuery):
    await db.remove_shortener_url(query.from_user.id)
    await query.answer("🗑 Shortener URL removed successfully!", show_alert=True)

# 🗑 Remove Caption (Popup)
@StreamBot.on_callback_query(filters.regex("^del_caption$"))
async def delete_caption(client, query: CallbackQuery):
    await db.remove_caption(query.from_user.id)
    await query.answer("🗑 Caption removed successfully!", show_alert=True)


    
#--------------------------------------- Save to Db --------------------------------------#

# ✅ Handle User Inputs
@StreamBot.on_message(filters.private & filters.text)
async def handle_user_input(client: Client, message: Message):
    """Handles user input when awaiting shortener API, URL, or caption."""

    user_id = message.from_user.id
    user_data = await db.get_user(user_id) or {}

    if "awaiting" not in user_data:
        return  # Ignore messages if no awaiting action is set

    awaiting = user_data["awaiting"]
    response_text = ""
    back_callback = "settings_menu"

    if awaiting == "shortener_api":
        await db.set_shortener_api(user_id, message.text)  
        response_text = f"✅ Shortener API set successfully!\n🔑 **API:** `{message.text}`"
        back_callback = "shortener_settings"

    elif awaiting == "shortener_url":
        await db.set_shortener_url(user_id, message.text)  
        response_text = f"✅ Shortener URL set successfully!\n🌐 **URL:** `{message.text}`"
        back_callback = "shortener_settings"

    elif awaiting == "caption":
        await db.set_caption(user_id, message.text)  
        response_text = f"✅ Caption set successfully!\n📝 **Caption:** `{message.text}`"
        back_callback = "caption_settings"

    await db.update_user_info(user_id, {"awaiting": None})

    if response_text:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=back_callback)]])
        await message.reply_text(response_text, reply_markup=keyboard)
        await asyncio.sleep(2)
        await message.delete()

#--------------------------------------- Connect Channel handler --------------------------------------#


#--------------------------------------- Channel Caption to Db --------------------------------------#
        

#--------------------------------------- Close Buttons--------------------------------------#

# ❌ Close Handler
@StreamBot.on_callback_query(filters.regex("^close$"))
async def close_message(client, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception as e:
        logger.exception(e)

@StreamBot.on_callback_query(filters.regex("^channel_settings$"))
async def channel_settings(client, query):
    """Shows the list of channels connected by a user."""
    user_id = query.from_user.id
    user_channels = await db.get_user_channels(user_id)

    print(f"🔍 DEBUG: User {user_id} has channels -> {user_channels}")  # ✅ Debug Log

    if not user_channels:
        channel_buttons = [[InlineKeyboardButton("❌ No Channels Connected", callback_data="none")]]
    else:
        channel_buttons = [
            [InlineKeyboardButton(f"📢 {channel['title']}", callback_data=f"view_channel_{channel['chat_id']}")]
            for channel in user_channels
        ]

    keyboard = InlineKeyboardMarkup([
        *channel_buttons,
        [InlineKeyboardButton("➕ Add Channel", callback_data="connect_channel")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_menu")]
    ])

    await query.message.edit_text(
        "📢 **Channel Settings**\n\nManage your connected channels and settings.",
        reply_markup=keyboard
    )

@StreamBot.on_callback_query(filters.regex("^connect_channel$"))
async def connect_channel(client, query):
    """Asks the user to forward a message from their channel to connect it."""
    user_id = query.from_user.id
    await db.update_user_info(user_id, {"awaiting": "connect_channel"})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="channel_settings")]])

    await query.message.edit_text(
        "🔹 **Forward any message from your channel to connect it.**\n\n"
        "📢 **Steps:**\n"
        "1️⃣ Open your **channel**\n"
        "2️⃣ **Forward a message** from the channel to this bot\n\n"
        "⚠️ **Bot must be an admin!**",
        reply_markup=keyboard
    )


@StreamBot.on_message(filters.private & filters.forwarded)
async def handle_forwarded_channel(client, message):
    """Handles forwarded messages and saves the channel ID."""
    
    user_id = message.from_user.id
    user_data = await db.get_user(user_id) or {}

    if user_data.get("awaiting") == "connect_channel":
        if not message.forward_from_chat or message.forward_from_chat.type != "channel":
            return await message.reply_text("⚠️ The forwarded message is not from a **channel**. Please try again.")

        chat_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title
        username = message.forward_from_chat.username or "Private Channel"

        print(f"🔍 DEBUG: Attempting to add Channel - {channel_title} ({chat_id}) for User {user_id}")  # ✅ Debug Log

        added = await db.add_channel(user_id, chat_id, channel_title, username)
        
        if added:
            print(f"✅ DEBUG: Channel {channel_title} successfully added to DB.")  # ✅ Debug Log
            await message.reply_text(
                f"✅ **Channel Connected Successfully!**\n\n"
                f"📡 **Channel:** `{channel_title}`\n"
                f"🆔 **Channel ID:** `{chat_id}`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="channel_settings")]])
            )
        else:
            print(f"⚠️ DEBUG: Channel {channel_title} is already added.")  # ✅ Debug Log
            await message.reply_text("⚠️ This channel is already connected!")

        await db.update_user_info(user_id, {"awaiting": None})

@StreamBot.on_callback_query(filters.regex("^view_channel_(.+)$"))
async def view_channel_settings(client, query):
    """Displays channel-specific API, URL, and caption settings."""
    user_id = query.from_user.id
    chat_id = int(query.matches[0].group(1))  # Extract channel ID from callback

    channel_data = await db.get_channel_details(user_id, chat_id)
    if not channel_data:
        return await query.answer("⚠️ Channel not found!", show_alert=True)

    shortener_api = channel_data.get("shortener_api", "❌ Not Set")
    shortener_url = channel_data.get("shortener_url", "❌ Not Set")
    caption = channel_data.get("caption", "❌ No Caption Set")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Set API", callback_data=f"set_api_{chat_id}"),
         InlineKeyboardButton("🌐 Set URL", callback_data=f"set_url_{chat_id}")],
        [InlineKeyboardButton("📝 Set Caption", callback_data=f"set_caption_{chat_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="channel_settings")]
    ])

    await query.message.edit_text(
        f"📢 **Channel Settings**\n\n"
        f"🆔 **Channel ID:** `{chat_id}`\n"
        f"🔑 **API:** `{shortener_api}`\n"
        f"🌐 **URL:** `{shortener_url}`\n"
        f"📝 **Caption:** `{caption}`",
        reply_markup=keyboard
    )


@StreamBot.on_callback_query(filters.regex("^set_api_(.+)$"))
async def set_channel_api(client, query):
    chat_id = int(query.matches[0].group(1))
    await db.update_user_info(query.from_user.id, {"awaiting": f"set_api_{chat_id}"})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"view_channel_{chat_id}")]])
    await query.message.edit_text("📌 Send the Shortener API key for this channel.", reply_markup=keyboard)

@StreamBot.on_callback_query(filters.regex("^set_url_(.+)$"))
async def set_channel_url(client, query):
    chat_id = int(query.matches[0].group(1))
    await db.update_user_info(query.from_user.id, {"awaiting": f"set_url_{chat_id}"})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"view_channel_{chat_id}")]])
    await query.message.edit_text("📌 Send the Shortener URL for this channel.", reply_markup=keyboard)

@StreamBot.on_callback_query(filters.regex("^set_caption_(.+)$"))
async def set_channel_caption(client, query):
    chat_id = int(query.matches[0].group(1))
    await db.update_user_info(query.from_user.id, {"awaiting": f"set_caption_{chat_id}"})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"view_channel_{chat_id}")]])
    await query.message.edit_text("📌 Send the custom caption for this channel.", reply_markup=keyboard)

@StreamBot.on_message(filters.private & filters.text)
async def handle_channel_inputs(client, message):
    user_id = message.from_user.id
    user_data = await db.get_user(user_id) or {}

    if not user_data.get("awaiting"):
        return  

    awaiting = user_data["awaiting"]
    response_text = ""
    back_callback = "channel_settings"

    if awaiting.startswith("set_api_"):
        chat_id = int(awaiting.split("_")[-1])
        await db.update_channel_info(user_id, chat_id, {"shortener_api": message.text})
        response_text = f"✅ API key saved for channel `{chat_id}`."
        back_callback = f"view_channel_{chat_id}"

    elif awaiting.startswith("set_url_"):
        chat_id = int(awaiting.split("_")[-1])
        await db.update_channel_info(user_id, chat_id, {"shortener_url": message.text})
        response_text = f"✅ Shortener URL saved for channel `{chat_id}`."
        back_callback = f"view_channel_{chat_id}"

    elif awaiting.startswith("set_caption_"):
        chat_id = int(awaiting.split("_")[-1])
        await db.update_channel_info(user_id, chat_id, {"caption": message.text})
        response_text = f"✅ Caption saved for channel `{chat_id}`."
        back_callback = f"view_channel_{chat_id}"

    await db.update_user_info(user_id, {"awaiting": None})
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=back_callback)]])
    await message.reply_text(response_text, reply_markup=keyboard)


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
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
        ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
        ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
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
