import logging

import discord
from discord.ext import commands

from src.utils.audio import AudioSearcher, create_audio_source

logger = logging.getLogger(__name__)


class Play(commands.Cog):
    """Reproduz audio a partir de uma busca multi-plataforma."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.searcher = AudioSearcher()

    @commands.command(
        name="play",
        aliases=["p"],
        help="Toca uma musica a partir de uma busca (YouTube > Spotify > SoundCloud > Deezer).",
    )
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            await ctx.reply("Entre em um canal de voz para usar este comando.", mention_author=False)
            return

        channel: discord.VoiceChannel = voice_state.channel
        voice = ctx.voice_client
        if voice and voice.channel != channel:
            await voice.move_to(channel)
        elif not voice:
            voice = await channel.connect()

        status_msg = await ctx.reply(f"Procurando `{query}`...", mention_author=False)
        result = await ctx.bot.loop.run_in_executor(None, self.searcher.search, query)

        if not result:
            await status_msg.edit(content="Nao encontrei resultados para sua busca.")
            return

        if voice.is_playing():
            voice.stop()

        source = create_audio_source(result)
        try:
            voice.play(
                discord.PCMVolumeTransformer(source, volume=0.65),
                after=lambda err: logger.error("Erro ao tocar audio: %s", err) if err else None,
            )
        except Exception as exc:  # pragma: no cover - voce runtime
            await status_msg.edit(content=f"Falha ao reproduzir: {exc}")
            return

        await status_msg.edit(
            content=f"Tocando **{result.title}** [{result.source.title()}] - {result.webpage_url}",
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Play(bot))
