from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional
from database import mongo
from utils.auth import verify_api_key_and_consume
from services.downloader import download_audio
from services.uploader import upload_audio_to_channel
from logging_ import LOGGER
import asyncio
import os
from datetime import datetime, timedelta

yt_mp3_router = APIRouter()
logger = LOGGER(__name__)

class YTResponse(BaseModel):
    success: bool
    video_id: str
    telegram_link: Optional[str] = None
    bitrate: int = 320
    cached: bool = False
    title: Optional[str] = None
    duration: Optional[int] = None

# processing collection name: "processing"
# audio_cache: "audio_cache"

@yt_mp3_router.get("/ytmp3/{api_key}/{video_id}", response_model=YTResponse)
async def get_ytmp3(api_key: str, video_id: str):
    # 1) validate API key
    api_key_doc = await verify_api_key_and_consume(api_key)
    if not api_key_doc:
        raise HTTPException(status_code=403, detail="Invalid or exhausted API key")

    # 2) check cache
    cached = await mongo.mongodb.audio_cache.find_one({"video_id": video_id})
    if cached:
        return YTResponse(
            success=True,
            video_id=video_id,
            telegram_link=cached["telegram_link"],
            cached=True,
            title=cached.get("title"),
            duration=cached.get("duration"),
        )

    # 3) Try to claim processing slot (avoid duplicate downloads)
    # We'll attempt to insert into processing collection; if duplicate, then poll cache
    try:
        await mongo.mongodb.processing.insert_one({"video_id": video_id, "status": "processing", "created_at": datetime.utcnow()})
        i_am_worker = True
    except Exception:
        # duplicate key or other -> someone else is processing
        i_am_worker = False

    if not i_am_worker:
        # poll for result (wait up to 60 seconds)
        timeout = datetime.utcnow() + timedelta(seconds=60)
        while datetime.utcnow() < timeout:
            doc = await mongo.mongodb.audio_cache.find_one({"video_id": video_id})
            if doc:
                return YTResponse(
                    success=True,
                    video_id=video_id,
                    telegram_link=doc["telegram_link"],
                    cached=True,
                    title=doc.get("title"),
                    duration=doc.get("duration"),
                )
            await asyncio.sleep(0.3)
        raise HTTPException(status_code=202, detail="Processing in progress. Retry later.")

    # 4) If this worker: do download + upload with concurrency control
    from main import concurrency_sem, bot  # local import to avoid circular early import
    async with concurrency_sem:
        try:
            out_path, meta = await download_audio(video_id)
            # ensure file exists and >0
            if not out_path or not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
                raise Exception("Downloaded file invalid")
            msg_link = await upload_audio_to_channel(bot, out_path, meta)
            # save to cache
            await mongo.mongodb.audio_cache.insert_one({
                "video_id": video_id,
                "telegram_link": msg_link,
                "title": meta.get("title"),
                "duration": meta.get("duration"),
                "bitrate": 320,
                "uploaded_at": datetime.utcnow()
            })
            return YTResponse(success=True, video_id=video_id, telegram_link=msg_link, cached=False, title=meta.get("title"), duration=meta.get("duration"))
        except Exception as e:
            logger.error(f"Processing failed for {video_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # remove processing lock
            await mongo.mongodb.processing.delete_one({"video_id": video_id})
