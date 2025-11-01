import asyncio
import os
import shlex
import json
from typing import Tuple
from datetime import datetime
from logging_ import LOGGER

logger = LOGGER(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def download_audio(video_id: str) -> Tuple[str, dict]:
    """
    Downloads audio using yt-dlp and returns (filepath, metadata)
    Metadata includes title, duration (seconds), ext
    """
    out_template = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    cmd = (
        f"yt-dlp -x --audio-format mp3 --audio-quality 0 "
        f"--embed-metadata --add-metadata --no-warnings "
        f"--print-json -o {shlex.quote(out_template)} https://youtu.be/{video_id}"
    )
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        logger.error(f"yt-dlp failed: {stderr.decode()}")
        raise Exception("yt-dlp download failed")

    # yt-dlp printed JSON lines — parse last JSON
    try:
        out_json = stdout.decode().strip().splitlines()[-1]
        meta = json.loads(out_json)
    except Exception:
        meta = {"title": video_id, "duration": None, "ext": "mp3"}
    # build path
    ext = meta.get("ext", "mp3")
    path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
    return path, {"title": meta.get("title"), "duration": meta.get("duration")}
