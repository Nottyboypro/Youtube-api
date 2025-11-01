import asyncio
from fastapi import FastAPI
from pyrogram import Client, idle
from routers import yt_mp3_router, admin_router
from config import API_ID, API_HASH, BOT_TOKEN, PORT, CONCURRENCY_LIMIT
from logging_ import LOGGER
from database.mongo import mongodb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.scheduler_tasks import daily_reset_job

LOGGER = LOGGER(__name__)
app = FastAPI(title="NottyBoy - YTMP3 to Telegram")

# Pyrogram bot client (session name "NottyBoyBot")
bot = Client("NottyBoyBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workdir=".")

# Shared concurrency semaphore
concurrency_sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

# include routers
app.include_router(yt_mp3_router, prefix="/")
app.include_router(admin_router, prefix="/admin")


@app.on_event("startup")
async def startup_event():
    LOGGER.info("Starting up: connecting bot and scheduler...")
    await bot.start()
    LOGGER.info("Pyrogram bot started")
    # create indexes for Mongo (safe if run multiple times)
    await mongodb.api_keys.create_index("api_key_hash", unique=True, sparse=True)
    await mongodb.audio_cache.create_index("video_id", unique=True)
    await mongodb.processing.create_index("video_id", unique=True)
    # start scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_reset_job, "cron", hour=0, minute=0)
    scheduler.start()
    LOGGER.info("Scheduler started (daily reset scheduled)")


@app.on_event("shutdown")
async def shutdown_event():
    LOGGER.info("Shutting down bot...")
    await bot.stop()


@app.get("/health")
async def health():
    # quick ping checks
    try:
        # mongo ping
        await mongodb.command("ping")
        bot_is_up = True if bot.is_connected else False
        return {"ok": True, "mongo": True, "bot_connected": bot_is_up}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Run uvicorn externally: uvicorn main:app --host 0.0.0.0 --port 8000
# Use idle() if you want to run the bot interactively; here FastAPI lifecycle manages bot
