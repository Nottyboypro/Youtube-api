from pyrogram import Client
from logging_ import LOGGER
import os

logger = LOGGER(__name__)

async def upload_audio_to_channel(bot: Client, file_path: str, meta: dict) -> str:
    """
    Uploads audio file to CHANNEL_ID and returns telegram link
    """
    from config import CHANNEL_ID, CHANNEL_USERNAME
    if not os.path.exists(file_path):
        raise Exception("file missing")
    # upload as audio for better playback
    msg = await bot.send_audio(chat_id=CHANNEL_ID, audio=file_path, caption=meta.get("title") or "")
    chat_username = CHANNEL_USERNAME.lstrip("@") if CHANNEL_USERNAME else None
    if chat_username:
        link = f"https://t.me/{chat_username}/{msg.message_id}"
    else:
        # fallback: construct using id (works only for public channels)
        link = f"https://t.me/c/{msg.chat.id}/{msg.message_id}"
    # cleanup file
    try:
        os.remove(file_path)
    except Exception:
        logger.warning("Failed to delete temp file")
    return link
