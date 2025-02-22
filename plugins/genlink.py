import re
import logging
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, DB_CHANNEL, NOTIFY_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
from plugins.imdb_api import get_poster  # Import IMDb poster fetching function
import os
import json
import requests
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    try:
        logger.info("📩 New file received!")

        username = (await bot.get_me()).username
        file_type = message.media

        # Extract title, quality, and language from file name
        file_name = message.document.file_name if message.document else message.video.file_name if message.video else "Unknown"
        logger.info(f"📂 File Name: {file_name}")

        match = re.match(r"(.+?)\s*(\d{4})?\s*(\d+p)?\s*([a-zA-Z]+)?", file_name)
        if match:
            title = match.group(1).strip()
            year = match.group(2) if match.group(2) else "Unknown"
            quality = match.group(3) if match.group(3) else "Unknown"
            language = match.group(4) if match.group(4) else "Unknown"
        else:
            title, year, quality, language = "Unknown", "Unknown", "Unknown", "Unknown"

        logger.info(f"🎬 Title: {title}, 🗓 Year: {year}, 📺 Quality: {quality}, 🗣 Language: {language}")

        # Fetch poster and IMDb data
        imdb_data = await get_poster(title, id=False)
        logger.info(f"🎞 IMDb Data Fetched: {imdb_data}")

        poster_url = imdb_data.get("poster", None)
        imdb_url = imdb_data.get("url", "")
        plot = imdb_data.get("plot", "No description available.")

        # Send file to DB_CHANNEL
        logger.info(f"📤 Sending file to DB_CHANNEL: {DB_CHANNEL}")
        db_message = await message.copy(DB_CHANNEL)
        file_id = str(db_message.id)
        logger.info(f"✅ File stored in DB_CHANNEL with ID: {file_id}")

        # Send notification to NOTIFY_CHANNEL
        notify_text = (f"**📢 New File Added**\n\n🎬 **Title:** {title}\n📅 **Year:** {year}\n🖥 **Quality:** {quality}\n🗣 **Language:** {language}\n\n📖 **Plot:** {plot}\n🔗 [IMDb Link]({imdb_url})")

        if poster_url:
            await bot.send_photo(NOTIFY_CHANNEL, poster_url, caption=notify_text)
            logger.info("✅ Poster sent to NOTIFY_CHANNEL")
        else:
            await bot.send_message(NOTIFY_CHANNEL, notify_text)
            logger.info("✅ Text notification sent to NOTIFY_CHANNEL")

        # Generate short link
        logger.info("🔗 Generating short link...")
        short_link = await get_short_link(file_id)
        if short_link:
            logger.info(f"✅ Short link generated: {short_link}")
        else:
            logger.warning("⚠️ Failed to generate short link!")

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Download", url=short_link if short_link else "#")],
            [InlineKeyboardButton("🔄 Share", switch_inline_query=title)]
        ])

        await message.reply_text(
            f"**✅ Your file is ready:**\n🎬 **{title}**\n📥 [Download]({short_link})",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        logger.info("✅ Reply sent to user")

    except Exception as e:
        logger.error(f"❌ Error in processing: {e}")
