import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

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
}

FFMPEG_BEFORE_OPTS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"


@dataclass
class SearchResult:
    title: str
    webpage_url: str
    stream_url: str
    source: str


class AudioSearcher:
    """Busca uma faixa em múltiplas plataformas em ordem de prioridade."""

    def __init__(self) -> None:
        self.search_order: Tuple[Tuple[str, str], ...] = (
            ("youtube", "ytsearch1"),
            ("spotify", "spsearch1"),
            ("soundcloud", "scsearch1"),
            ("deezer", "dzsearch1"),
        )

    def search(self, query: str) -> Optional[SearchResult]:
        for source, prefix in self.search_order:
            result = self._search_platform(prefix, query, source)
            if result:
                return result
        return None

    def _search_platform(self, search_prefix: str, query: str, source: str) -> Optional[SearchResult]:
        search_query = f"{search_prefix}:{query}"
        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(search_query, download=False)
        except Exception as exc:
            logger.warning("Falha ao buscar em %s: %s", source, exc)
            return None

        if not info:
            return None

        entry = info["entries"][0] if "entries" in info else info
        stream_url = entry.get("url")
        title = entry.get("title")
        webpage_url = entry.get("webpage_url") or entry.get("original_url") or stream_url

        if not stream_url or not title:
            return None

        return SearchResult(
            title=title,
            webpage_url=webpage_url or stream_url,
            stream_url=stream_url,
            source=source,
        )


def create_audio_source(result: SearchResult) -> discord.AudioSource:
    """Cria uma fonte de audio via FFmpeg para streaming."""
    executable = ensure_ffmpeg_binary()
    return discord.FFmpegPCMAudio(
        result.stream_url,
        executable=executable,
        before_options=FFMPEG_BEFORE_OPTS,
        options="-vn",
    )
