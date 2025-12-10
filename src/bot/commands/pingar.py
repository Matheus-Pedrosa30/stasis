import asyncio

from discord.ext import commands


class Pingar(commands.Cog):
    """Envia mencoes repetidas com limite."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="pingar",
        help="pingar <@usuario> <vezes> [silent]: envia mencoes com contador (limite 150).",
        extras={"category": "spam"},
    )
    async def pingar(self, ctx: commands.Context, mention: str, times: int, silent: bool | None = None) -> None:
        count = max(1, min(times, 150))
        resolved_silent = silent if silent is not None else count > 5
        delete_after = 0.5 if resolved_silent else None

        status = await ctx.reply("Pingando...", mention_author=False)
        try:
            await status.add_reaction("❌")
        except Exception:
            pass  # permissao pode faltar, mas nao quebra o comando

        cancel_event = asyncio.Event()

        async def watch_cancel() -> None:
            try:
                await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: (
                        user.id == ctx.author.id
                        and reaction.message.id == status.id
                        and str(reaction.emoji) == "❌"
                    ),
                    timeout=None,
                )
                cancel_event.set()
            except asyncio.CancelledError:
                return

        watcher = asyncio.create_task(watch_cancel())

        sent = 0
        for idx in range(1, count + 1):
            if cancel_event.is_set():
                break
            try:
                await ctx.send(f"{mention} ({idx}/{count})", delete_after=delete_after)
                sent = idx
            except Exception:
                await asyncio.sleep(0.3)
                continue
            # reduz chances de rate limit
            await asyncio.sleep(0.2 if count > 30 or resolved_silent else 0.05)

        watcher.cancel()

        if cancel_event.is_set():
            await status.edit(content=f"Pingado {sent}/{count} (cancelado).")
        else:
            await status.edit(content=f"Pingado {sent}/{count}.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pingar(bot))
