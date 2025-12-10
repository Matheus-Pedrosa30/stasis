import asyncio
import logging
from collections import deque
from typing import Deque, Dict, Optional, Tuple

import discord
from discord.ext import commands

from src.utils.audio import (
    SearchResult,
    create_audio_source,
    ensure_ffmpeg_binary_async,
    search_youtube,
)

logger = logging.getLogger(__name__)


class Music(commands.Cog):
    """Comando de musica com fila basica."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # fila: guild_id -> deque[(SearchResult, discord.abc.Messageable)]
        self.queues: Dict[int, Deque[Tuple[SearchResult, discord.abc.Messageable]]] = {}

    def _get_queue(self, guild_id: int) -> Deque[Tuple[SearchResult, discord.abc.Messageable]]:
        return self.queues.setdefault(guild_id, deque())

    async def _ensure_voice(self, ctx: commands.Context) -> Optional[discord.VoiceClient]:
        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            await ctx.reply("Entre em um canal de voz para usar este comando.", mention_author=False)
            return None

        channel: discord.VoiceChannel = voice_state.channel
        voice = ctx.voice_client
        if voice and voice.channel != channel:
            await voice.move_to(channel)
        elif not voice:
            voice = await channel.connect()
        return voice

    async def _play_next(self, guild: discord.Guild, voice: discord.VoiceClient) -> None:
        queue = self._get_queue(guild.id)
        if not queue:
            return

        next_track, channel = queue[0]
        try:
            ffmpeg_exec = await asyncio.wait_for(ensure_ffmpeg_binary_async(), timeout=25)
        except Exception as exc:
            logger.error("Falha ao resolver FFmpeg: %s", exc)
            queue.popleft()
            try:
                await channel.send("Falha ao preparar FFmpeg. Tente novamente.")
            except Exception:
                pass
            return

        source = create_audio_source(next_track, executable=ffmpeg_exec)
        wrapped = discord.PCMVolumeTransformer(source, volume=0.65)

        def after_play(err: Exception | None) -> None:
            if err:
                logger.error("Erro ao tocar audio: %s", err)
            proc = getattr(source, "_process", None)
            rc = None
            stderr_out = ""
            if proc:
                try:
                    if proc.poll() is None:
                        proc.wait(timeout=5)
                    rc = proc.returncode
                    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
                except Exception:
                    pass

            if rc not in (0, None):
                logger.error("FFmpeg saiu com codigo %s", rc)
                if stderr_out:
                    logger.error("FFmpeg stderr: %s", stderr_out.strip())
                try:
                    self.bot.loop.create_task(
                        channel.send(f"Erro ao reproduzir **{next_track.title}**. Retornou codigo {rc}.")
                    )
                except Exception:
                    pass
            queue.popleft()
            # Aciona proxima faixa, se houver
            if queue:
                try:
                    self.bot.loop.create_task(self._play_next(guild, voice))
                except Exception as exc:
                    logger.error("Falha ao agendar proxima faixa: %s", exc)

        try:
            voice.play(wrapped, after=after_play)
        except Exception as exc:  # pragma: no cover
            logger.error("Falha ao iniciar playback: %s", exc)
            queue.popleft()
            return

    @commands.command(
        name="play",
        aliases=["p"],
        help="Toca audio do YouTube. Uso: play <busca>",
        extras={"category": "musica"},
    )
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        voice = await self._ensure_voice(ctx)
        if not voice:
            return

        status = await ctx.reply(f"Procurando `{query}`...", mention_author=False)
        try:
            result = await asyncio.wait_for(
                ctx.bot.loop.run_in_executor(None, search_youtube, query),
                timeout=15,
            )
        except asyncio.TimeoutError:
            await status.edit(content="Busca demorou demais. Tente novamente.")
            return

        if not result:
            await status.edit(content="Nao encontrei resultados para sua busca.")
            return

        queue = self._get_queue(ctx.guild.id)
        queue.append((result, ctx.channel))

        if not voice.is_playing() and not voice.is_paused():
            await status.edit(content=f"Tocando **{result.title}** - {result.webpage_url}")
            await self._play_next(ctx.guild, voice)
        else:
            await status.edit(content=f"Adicionado a fila: **{result.title}** - {result.webpage_url}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
