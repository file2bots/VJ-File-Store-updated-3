import re
import logging
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from plugins.dbusers import unpack_new_file_id
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_size, gen_link, clean_title, get_poster, temp, short_link
from config import HOW_TO_POST_SHORT, ADMINS, DIRECT_GEN_DB

user_states = {}

async def delete_previous_reply(chat_id):
    if chat_id in user_states and "last_reply" in user_states[chat_id]:
        try:
            await user_states[chat_id]["last_reply"].delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

@Client.on_message(filters.command("post") & filters.user(ADMINS))
async def post_command(client, message):
    try:
        await message.reply("**Wᴇʟᴄᴏᴍᴇ Tᴏ Oᴜʀ Rᴀʀᴇ Mᴏᴠɪᴇ Pᴏsᴛ Fᴇᴀᴛᴜʀᴇ🙂**\n\n"
                            "**👉🏻Sᴇɴᴅ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ғɪʟᴇs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ👈🏻**\n\n"
                            "**‼️ Nᴏᴛᴇ: Oɴʟʏ ɴᴜᴍʙᴇʀ**", disable_web_page_preview=True)
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
                        rply = await message.reply("⏩ Fᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ")
                        user_states[chat_id]["last_reply"] = rply
                        return

                    user_states[chat_id] = {
                        "state": "awaiting_files",
                        "num_files": num_files,
                        "files_received": 0,
                        "file_ids": [],
                        "file_sizes": []
                    }
                    reply_message = await message.reply("**⏩ Fᴏʀᴡᴀʀᴅ ᴛʜᴇ ɴᴏ: 1 ғɪʟᴇ**")
                    user_states[chat_id]["last_reply"] = reply_message
                except ValueError:
                    await message.reply("Invalid input. Please enter a valid number.")

            elif current_state == "awaiting_files":
                file_id = None
                size = "Unknown"

                if message.document:
                    file_id = unpack_new_file_id(message.document.file_id)
                    size = get_size(message.document.file_size)
                elif message.video:
                    file_id = unpack_new_file_id(message.video.file_id)
                    size = get_size(message.video.file_size)

                if file_id:
                    user_states[chat_id]["file_ids"].append(file_id)
                    user_states[chat_id]["file_sizes"].append(size)

                user_states[chat_id]["files_received"] += 1
                files_received = user_states[chat_id]["files_received"]
                num_files_left = user_states[chat_id]["num_files"] - files_received

                if num_files_left > 0:
                    reply_message = await message.reply(f"**⏩ Fᴏʀᴡᴀʀᴅ ᴛʜᴇ ɴᴏ: {files_received + 1} ғɪʟᴇ**")
                    user_states[chat_id]["last_reply"] = reply_message
                else:
                    reply_message = await message.reply("**ɴᴏᴡ sᴇɴᴅ ᴛʜᴇ ɴᴀᴍᴇ ᴏғ ᴛʜᴇ ᴍᴏᴠɪᴇ (ᴏʀ) ᴛɪᴛʟᴇ**")
                    user_states[chat_id]["state"] = "awaiting_title"
                    user_states[chat_id]["last_reply"] = reply_message

            elif current_state == "awaiting_title":
                title = message.text.strip()
                title_clean = re.sub(r"[()\[\]{}:;'!]", "", title)
                cleaned_title = clean_title(title_clean)

                resolution_match = re.search(r"(\d{3,4}p)", title, re.IGNORECASE)
                resolution = resolution_match.group(1) if resolution_match else "Unknown"

                imdb_data = await get_poster(cleaned_title)
                poster = imdb_data.get('poster') if imdb_data else None

                buttons = []
                for i, file_id in enumerate(user_states[chat_id]["file_ids"]):
                    long_url = f"https://t.me/{temp.U_NAME}?start=file_{file_id[0]}"
                    short_link_url = await short_link(long_url)
                    if not short_link_url.startswith("http"):
                        short_link_url = "https://example.com"  # Fallback URL
                    btn_text = f"{user_states[chat_id]['file_sizes'][i]} ({resolution}) 🔗"
                    buttons.append([InlineKeyboardButton(btn_text, url=short_link_url)])

                keyboard = InlineKeyboardMarkup(buttons)
                summary_message = f"**🎬 {title} Tamil HDRip**\n\n" \
                                  f"**[ 𝟹𝟼𝟶ᴘ☆𝟺𝟾𝟶ᴘ☆Hᴇᴠᴄ☆𝟽𝟸𝟶ᴘ☆𝟷𝟶𝟾𝟶ᴘ ]✌**\n\n" \
                                  f"**✅ Note: [Hᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ]({HOW_TO_POST_SHORT})👀**\n\n" \
                                  f"**Mᴏᴠɪᴇ Gʀᴏᴜᴘ 𝟸𝟺/𝟽: @Roxy_Request_24_7**\n\n" \
                                  f"**❤️‍🔥ー𖤍 𓆩 Sʜᴀʀᴇ Wɪᴛʜ Fʀɪᴇɴᴅs 𓆪 𖤍ー❤️‍🔥**"

                if poster:
                    await message.reply_photo(poster, caption=summary_message, reply_markup=keyboard)
                else:
                    await message.reply(summary_message, reply_markup=keyboard)

                await message.delete()
                del user_states[chat_id]
    except Exception as e:
        await message.reply(f"Error occurred: {e}")
