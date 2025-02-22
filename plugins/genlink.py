import re
import logging
from pyrogram import filters, Client, enums
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, DB_CHANNEL, NOTIFY_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
from plugins.imdb_api import get_poster  # Import IMDb poster fetching function
import os
import json
import requests
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

async def send_msg(bot, filename, caption): 
    try:
        filename = re.sub(r'\(\@\S+\)|\[\@\S+\]|\b@\S+|\bwww\.\S+', '', filename).strip()
        caption = re.sub(r'\(\@\S+\)|\[\@\S+\]|\b@\S+|\bwww\.\S+', '', caption).strip()
        
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else "Unknown"

        qualities = ["ORG", "hdcam", "HQ", "HDRip", "camrip", "hdtc", "predvd", "DVDscr", "dvdrip", "HDTC", "HDTS"]
        quality = await get_qualities(caption.lower(), qualities) or "HDRip"

        language = "English"  # Default assumption, modify logic to detect

        imdb = await get_poster(filename, id=False)
        poster_url = imdb.get("poster", None)
        imdb_url = imdb.get("url", "")
        plot = imdb.get("plot", "IMDb Data Not Available.")

        text = f"**📢 New File Added**\n\n🎬 **Title:** {filename}\n📅 **Year:** {year}\n🖥 **Quality:** {quality}\n🗣 **Language:** {language}\n\n📖 **Plot:** {plot}\n🔗 [IMDb Link]({imdb_url})"
        
        btn = [[InlineKeyboardButton('🌲 Get Files 🌲', url=f"https://telegram.me/{bot.username}?start=getfile-{filename.replace(' ', '-')}")]]
        
        if poster_url:
            await bot.send_photo(NOTIFY_CHANNEL, poster_url, caption=text, reply_markup=InlineKeyboardMarkup(btn))
        else:              
            await bot.send_message(NOTIFY_CHANNEL, text, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        logger.error(f"❌ Error in send_msg: {e}")

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    try:
        logger.info("📩 New file received!")

        file_name = message.document.file_name if message.document else message.video.file_name if message.video else "Unknown"
        logger.info(f"📂 File Name: {file_name}")

        # Send file to DB_CHANNEL
        try:
            logger.info(f"📤 Sending file to DB_CHANNEL: {DB_CHANNEL}")
            db_message = await message.copy(DB_CHANNEL)
            file_id = str(db_message.id)
            logger.info(f"✅ File stored in DB_CHANNEL with ID: {file_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send file to DB_CHANNEL: {e}")
            return

        # Send notification using send_msg
        await send_msg(bot, file_name, file_name)

        # Generate short link
        logger.info("🔗 Generating short link...")
        try:
            short_link = await get_short_link(file_id)
            if short_link:
                logger.info(f"✅ Short link generated: {short_link}")
            else:
                logger.warning("⚠️ Failed to generate short link!")
        except Exception as e:
            logger.error(f"❌ Short link generation failed: {e}")
            short_link = "#"

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Download", url=short_link if short_link else "#")],
            [InlineKeyboardButton("🔄 Share", switch_inline_query=file_name)]
        ])

        await message.reply_text(
            f"**✅ Your file is ready:**\n🎬 **{file_name}**\n📥 [Download]({short_link})",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        logger.info("✅ Reply sent to user")
    except Exception as e:
        logger.error(f"❌ Error in processing: {e}")
        logger.exception(e)  # Logs full traceback for debugging
