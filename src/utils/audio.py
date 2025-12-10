import asyncio
import logging
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional

import discord
from yt_dlp import YoutubeDL

from src.utils.ffmpeg_loader import ensure_ffmpeg_binary

logger = logging.getLogger(__name__)

YDL_OPTS: Dict[str, object] = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "nocheckcertificate": True,
    "skip_download": True,
    "socket_timeout": 10,
    "retries": 1,
}

FFMPEG_BEFORE_OPTS = (
    "-nostdin -hide_banner -loglevel error "
    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
    "-protocol_whitelist file,http,https,tcp,tls,crypto"
)


@dataclass
class SearchResult:
    title: str
    webpage_url: str
    stream_url: str
    source: str
    http_headers: Dict[str, str]
    duration: Optional[float] = None


def search_youtube(query: str) -> Optional[SearchResult]:
    search_query = f"ytsearch1:{query}"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(search_query, download=False)
    except Exception as exc:
        logger.warning("Falha ao buscar no YouTube: %s", exc)
        return None

    if not info:
        return None

    entry = info["entries"][0] if "entries" in info else info
    stream_url = entry.get("url")
    title = entry.get("title")
    webpage_url = entry.get("webpage_url") or entry.get("original_url") or stream_url
    http_headers = entry.get("http_headers") or {}
    duration = entry.get("duration")

    if not stream_url or not title:
        return None

    return SearchResult(
        title=title,
        webpage_url=webpage_url or stream_url,
        stream_url=stream_url,
        source="youtube",
        http_headers=http_headers,
        duration=duration,
    )


def create_audio_source(result: SearchResult, executable: Optional[str] = None) -> discord.AudioSource:
    """Cria uma fonte de audio via FFmpeg para streaming."""
    executable = executable or ensure_ffmpeg_binary()
    headers_opt = ""
    if result.http_headers:
        header_lines = "".join(f"{k}: {v}\r\n" for k, v in result.http_headers.items())
        headers_opt = f' -headers "{header_lines}"'
    return discord.FFmpegPCMAudio(
        result.stream_url,
        executable=executable,
        before_options=f"{FFMPEG_BEFORE_OPTS}{headers_opt}",
        options="-vn",
        stderr=subprocess.PIPE,
    )


async def ensure_ffmpeg_binary_async() -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, ensure_ffmpeg_binary)
