import discord
from discord.ext import commands


class Ping(commands.Cog):
    """Comando simples de latência."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping", help="Responde com a latência do bot.")
    async def ping(self, ctx: commands.Context) -> None:
        latency_ms = self.bot.latency * 1000
        await ctx.reply(f"Pong! {latency_ms:.0f}ms", mention_author=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
