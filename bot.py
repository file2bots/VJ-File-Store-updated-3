

import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script 
from datetime import date, datetime 
import pytz
from aiohttp import web
from CloudXbotz.server import web_server
from utils import temp #


import asyncio
from pyrogram import idle
from CloudXbotz.bot import StreamBot
from CloudXbotz.utils.keepalive import ping_server
from CloudXbotz.bot.clients import initialize_clients


ppath = "plugins/*.py"
files = glob.glob(ppath)
StreamBot.start()
loop = asyncio.get_event_loop()

async def start():
    print('\n')
    print('Initalizing CloudXbotz Bot')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("CloudXbotz Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    me = await StreamBot.get_me()
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    app = web.AppRunner(await web_server())
    await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    if CLONE_MODE == True:
        await restart_bots()
    print("Bot Started Powered By @CloudXbotz")
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')

from pyrogram import Client, filters
from plugins.utils.imdb import get_imdb_details  # <- create this file
from database.ia_filterdb import save_file_data  # <- create or confirm this

@Client.on_message(filters.channel & filters.document | filters.video)
async def auto_post_handler(client, message):
    if str(message.chat.id) != str(DATABASE_CHANNEL_ID):
        return  # Only listen to your DB channel

    file_name = message.document.file_name if message.document else message.video.file_name
    title = extract_title_from_filename(file_name)  # <- write this helper

    imdb_data = await get_imdb_details(title)
    await save_file_data(message, imdb_data)

    caption = generate_caption(imdb_data)
    buttons = [[InlineKeyboardButton("📥 Get Link", url=f"https://t.me/{BOT_USERNAME}?start={title.replace(' ', '_')}")]]

    await client.send_photo(
        chat_id=UPDATE_CHANNEL_ID,
        photo=imdb_data.get("poster", ""),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
