import motor.motor_asyncio
import datetime
from config import DB_NAME, DB_URI
from datetime import timedelta

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.links = self.db.links
        self.users = self.db.users
        self.channels = self.db.channels  # ✅ Added Channel Collection

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            join_date=datetime.date.today().isoformat(),
            shortener_api=None,  # ✅ Consistent naming
            shortener_url=None,  # ✅ Consistent naming
            awaiting=None,  # ✅ Used for user interactions
            caption=None,
           # premium_expires=None,
            shortener_enabled=False,
           # connected_channel=None,  # ✅ Added Channel Storage
            #channel_caption=None  # ✅ Added Custom Caption for Channel
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

#------------SETTINGS CAPTION--------------------#

    async def hs_add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)



    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count

    async def add_user_pass(self, id, ag_pass):
        await self.add_user(int(id))
        await self.col.update_one({"id": int(id)}, {"$set": {"ag_p": ag_pass}})

    async def get_user_pass(self, id):
        user_pass = await self.col.find_one({"id": int(id)})
        return user_pass.get("ag_p", None) if user_pass else None

    

    async def get_all_chats(self):
        return self.grp.find({})


   # async def get_user(self, id):
     #   """Fetch a user's data from the database."""
       # user = await self.col.find_one({"id": int(id)}) or {}
       # return user  

    #async def update_user_info(self, user_id, value: dict, tag="$set"):
     #   """Updates user information in the database."""
       # await self.col.update_one({"id": int(user_id)}, {tag: value})

    # 📌 Shortener API Functions
    async def set_shortener_api(self, user_id, api_key):
        """Set or update the shortener API key."""
        await self.update_user_info(user_id, {"shortener_api": api_key})

    async def get_shortener_api(self, user_id):
        """Retrieve the shortener API key."""
        user = await self.get_user(user_id)
        return user.get("shortener_api", "❌ No API Set")

    async def remove_shortener_api(self, user_id):
        """Remove the shortener API key."""
        await self.update_user_info(user_id, {"shortener_api": None})

    async def set_shortener_url(self, user_id, url):
        """Set or update the shortener URL."""
        await self.update_user_info(user_id, {"shortener_url": url})

    async def get_shortener_url(self, user_id):
        """Retrieve the shortener URL."""
        user = await self.get_user(user_id)
        return user.get("shortener_url", "❌ No URL Set")

    async def remove_shortener_url(self, user_id):
        """Remove the shortener URL."""
        await self.update_user_info(user_id, {"shortener_url": None})

    async def toggle_shortener(self, user_id, status: bool):
        """Enable or disable the shortener."""
        await self.update_user_info(user_id, {"shortener_enabled": status})

    # 📌 Caption Functions
    async def set_caption(self, user_id, caption_text):
        """Set or update the caption."""
        await self.update_user_info(user_id, {"caption": caption_text})

    async def get_caption(self, user_id):
        """Retrieve the stored caption."""
        user = await self.get_user(user_id)
        return user.get("caption", "❌ No Caption Set")

    async def remove_caption(self, user_id):
        """Remove the stored caption."""
        await self.update_user_info(user_id, {"caption": None})
    

    async def add_user(self, id):
        if not await self.users.find_one({"id": id}):
            await self.users.insert_one(self.new_user(id))

    async def get_user(self, id):
        return await self.users.find_one({"id": id}) or {}

    async def update_user_info(self, user_id, value: dict, tag="$set"):
        await self.users.update_one({"id": user_id}, {tag: value})

    # --------------------------------- 📢 CHANNEL DATABASE FUNCTIONS --------------------------------- #

    async def in_channel(self, user_id: int, chat_id: int) -> bool:
        """Check if a user has already added this channel."""
        return bool(await self.channels.find_one({"user_id": user_id, "chat_id": chat_id}))

    # ✅ Add channel to the database
    async def add_channel(self, user_id, chat_id, title, username):
        """Adds a channel to the database and logs debug information."""
        existing_channel = await self.channels.find_one({"user_id": user_id, "chat_id": chat_id})
    
        if existing_channel:
            print(f"🔍 DEBUG: Channel {chat_id} already exists for User {user_id}")  # ✅ Debug Log
            return False  # Channel already exists

        channel_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "title": title,
            "username": username,
            "shortener_api": None,
            "shortener_url": None,
            "caption": None
        }

        try:
            result = await self.channels.insert_one(channel_data)
            print(f"✅ DEBUG: Channel {chat_id} successfully added for User {user_id} with ID {result.inserted_id}")  # ✅ Debug Log
            return True
        except Exception as e:
            print(f"⚠️ DEBUG: Error adding channel {chat_id} for User {user_id}: {e}")  # ✅ Debug Log
            return False

    async def remove_channel(self, user_id: int, chat_id: int):
        """Remove a channel from the database."""
        if not await self.in_channel(user_id, chat_id):
            return False
        return await self.channels.delete_many({"user_id": user_id, "chat_id": chat_id})

    async def get_channel_details(self, user_id, chat_id):
        """Fetch a specific channel's details."""
        return await self.channels.find_one({"user_id": user_id, "chat_id": chat_id})

    # ✅ Get all channels connected by a user
    async def get_user_channels(self, user_id):
        """Fetch all channels connected by a user."""
        channels_cursor = self.channels.find({"user_id": user_id})
        return [channel async for channel in channels_cursor]

    async def update_channel_info(self, user_id, chat_id, value: dict, tag="$set"):
        """Update channel-related settings."""
        await self.channels.update_one({"user_id": user_id, "chat_id": chat_id}, {tag: value})

    async def remove_channel_caption(self, user_id, chat_id):
        """Remove the saved channel caption."""
        await self.channels.update_one({"user_id": user_id, "chat_id": chat_id}, {"$unset": {"caption": ""}})
    

    #--------------------------------------- Channel --------------------------------------#

   # async def set_connected_channel(self, user_id, channel_id):
      #  """Saves the connected channel ID to the database."""
       # print(f"✅ DEBUG: Saving Channel {channel_id} for User {user_id}")  # ✅ Log storing
       # await self.col.update_one({"id": int(user_id)}, {"$set": {"connected_channel": channel_id}},upsert=True)
        
   # async def get_connected_channel(self, user_id):
      #  """Fetches the connected channel ID."""
       # user = await self.get_user(user_id)
        #channel_id = user.get("connected_channel", None)
       # print(f"✅ DEBUG: Retrieved Channel -> {channel_id} for User {user_id}")  # ✅ Log retrieval
        #return channel_id

    #async def remove_connected_channel(self, user_id):
   #     """Removes the connected channel from the user's data."""
      #  await self.col.update_one({"id": int(user_id)}, {"$unset": {"connected_channel": ""}})

  #  async def set_channel_caption(self, user_id, caption):
       # """Set a custom caption for the connected channel."""
       # await self.col.update_one({"id": int(user_id)}, {"$set": {"channel_caption": caption}}, upsert=True)

    #async def get_channel_caption(self, user_id):
        #"""Retrieve the custom channel caption."""
       # user = await self.get_user(user_id)
       # return user.get("channel_caption", None)

    #async def remove_channel_caption(self, user_id):
       # """Removes the saved channel caption."""
       # await self.col.update_one({"id": int(user_id)}, {"$unset": {"channel_caption": ""}})



db = Database(DB_URI, DB_NAME)
