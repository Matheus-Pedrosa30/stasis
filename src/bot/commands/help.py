from collections import defaultdict
from typing import Dict, List, Set

from discord.ext import commands


class Help(commands.Cog):
    """Help customizado com categorias."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["ajuda"],
        help="help [categoria]: lista comandos por categoria.",
    )
    async def help_cmd(self, ctx: commands.Context, categoria: str | None = None) -> None:
        prefix = ctx.prefix or "s!"

        # Agrupa comandos por categoria definida em extras["category"]
        categories: Dict[str, List[commands.Command]] = defaultdict(list)
        for cmd in self.bot.walk_commands():
            if cmd.hidden:
                continue
            cat = (cmd.extras or {}).get("category", "geral")
            categories[cat].append(cmd)

        if categoria is None:
            lines = [f"Comandos por categoria (use `{prefix}help <categoria>`):"]
            for cat, cmds in sorted(categories.items()):
                names = ", ".join(sorted(c.qualified_name for c in cmds))
                lines.append(f"- {cat}: {names}")
            await ctx.reply("\n".join(lines), mention_author=False)
            return

        categoria = categoria.lower()
        cmds = categories.get(categoria)
        if not cmds:
            available_cats = ", ".join(sorted(categories.keys()))
            await ctx.reply(
                f"Categoria '{categoria}' nao encontrada. Disponiveis: {available_cats}.",
                mention_author=False,
            )
            return

        lines = [f"Categoria: {categoria}"]
        for cmd in sorted(cmds, key=lambda c: c.qualified_name):
            usage = f"{prefix}{cmd.qualified_name} {cmd.signature}".strip()
            help_text = cmd.help or "Sem descricao."
            lines.append(f"- {usage}: {help_text}")

        await ctx.reply("\n".join(lines), mention_author=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
