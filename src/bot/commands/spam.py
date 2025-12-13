import asyncio
import os
import re

from discord.ext import commands


CANCEL_EMOJI = "❌"


class Spam(commands.Cog):
    """Send repeated mentions with a limit."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="spam",
        aliases=["spammention"],
        help="spam <@user> <times> [silent]: sends repeated mentions (limit 150).",
        extras={"category": "spam"},
    )
    async def spam(self, ctx: commands.Context, mention: str, times: int, silent: bool | None = None) -> None:
        blocked_id = os.getenv("SPAM_BLOCK_USER_ID")
        if blocked_id:
            match = re.search(r"\d+", mention)
            if match and match.group(0) == blocked_id:
                await ctx.reply("This user is blocked from spam mentions.", mention_author=False)
                return

        count = max(1, min(times, 150))
        resolved_silent = silent if silent is not None else count > 5
        delete_after = 0.5 if resolved_silent else None

        status = await ctx.reply("Spamming...", mention_author=False)
        try:
            await status.add_reaction(CANCEL_EMOJI)
        except Exception:
            pass  # missing perms are non-blocking

        cancel_event = asyncio.Event()

        async def watch_cancel() -> None:
            try:
                await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: (
                        user.id == ctx.author.id
                        and reaction.message.id == status.id
                        and str(reaction.emoji) == CANCEL_EMOJI
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

        watcher.cancel()

        if cancel_event.is_set():
            await status.edit(content=f"Spammed {sent}/{count} (cancelled).")
        else:
            await status.edit(content=f"Spammed {sent}/{count}.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Spam(bot))
