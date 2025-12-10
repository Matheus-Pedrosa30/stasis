import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Iterable

import discord
from discord.ext import commands

from src.utils.logging_config import setup_logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Garante que o pacote src/ seja importavel mesmo quando rodando o arquivo diretamente.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
DEFAULT_ENV_PATH = BASE_DIR / "config" / ".env"
COMMANDS_DIR = Path(__file__).resolve().parent / "commands"
COMMANDS_PACKAGE = "src.bot.commands"


def load_dotenv(path: Path = DEFAULT_ENV_PATH) -> None:
    """Carrega um arquivo .env simples (KEY=VALUE) para o ambiente."""
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _discover_commands(directory: Path = COMMANDS_DIR) -> Iterable[str]:
    for file in sorted(directory.glob("*.py")):
        if file.stem.startswith("__"):
            continue
        yield f"{COMMANDS_PACKAGE}.{file.stem}"


async def _load_extensions(bot: commands.Bot) -> None:
    for ext in _discover_commands():
        await bot.load_extension(ext)


async def run_bot() -> None:
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("Defina DISCORD_BOT_TOKEN no ambiente ou em um arquivo .env.")
    prefix = os.getenv("DISCORD_BOT_PREFIX", "s!")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=prefix,
        intents=intents,
        description="Bot do Discord",
        help_command=None,  # usamos help customizado
    )
    await _load_extensions(bot)

    setup_logging(logging.INFO)

    async with bot:
        await bot.start(token)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
