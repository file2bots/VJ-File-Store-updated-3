import sys
import glob
import importlib
import asyncio
import logging
import logging.config
from pathlib import Path
from pyrogram import idle, Client
from aiohttp import web
import pytz
from datetime import date, datetime

# 🔧 Importing Required Modules
from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from Script import script
from CloudXbotz.server import web_server
from CloudXbotz.bot import StreamBot
from CloudXbotz.utils.keepalive import ping_server
from CloudXbotz.bot.clients import initialize_clients
from utils import temp

# 📌 Load Logging Configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# 📂 Load Plugins
ppath = "plugins/*.py"
files = glob.glob(ppath)

# 🔄 Async Startup Function
async def start():
    print("\n🔄 Initializing CloudXbotz Bot...")
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username

    # ✅ Initialize Client Sessions
    await initialize_clients()

    # ✅ Load Plugins Dynamically
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
            print(f"✅ CloudXbotz Plugin Loaded: {plugin_name}")

    # ✅ Keep Heroku Dyno Alive
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # ✅ Bot Information
    me = await StreamBot.get_me()
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    # ✅ Send Restart Notification
    await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))

    # ✅ Start Web Server
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()

    # ✅ Clone Mode Handling
    if CLONE_MODE:
        await restart_bots()

    print("🚀 Bot Started Successfully | Powered by @CloudXbotz")
    await idle()  # Keep Bot Running

# 🚀 Run the Bot with Async-Safe Method
if __name__ == "__main__":
    try:
        asyncio.run(start())  # ✅ Ensures clean startup & shutdown
    except KeyboardInterrupt:
        logging.info("🛑 Bot Stopped | Goodbye! 👋")
