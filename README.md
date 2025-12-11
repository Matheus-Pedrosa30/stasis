# Open Source Discord Bot

Python bot built with `discord.py`, modular structure for easy maintenance and extension.

## Structure
- `src/bot/main.py`: bot bootstrap, loads extensions and logging.
- `src/bot/commands/`: one file per command (e.g., `ping`, `pingar`, `help`, `play`).
- `src/utils/`: shared utilities (logging, FFmpeg loader, audio helpers).
- `config/example.env`: sample env vars; copy to `config/.env`.
- `requirements.txt`: dependencies.
- Scripts: `install.bat` (sets up Python 3.11 venv + deps), `start_bot.bat` (persistent console), `stop_bot.bat` (kills running bot).

## Prerequisites
- Python 3.11+
- Discord bot token from the Developer Portal (`DISCORD_BOT_TOKEN`).
- FFmpeg available or set `FFMPEG_BINARY` (Windows auto-downloads if missing).
- `PyNaCl` for voice (already in `requirements.txt`).

## Setup
1) Quick setup (recommended):
   ```cmd
   install.bat
   ```
   Creates `.venv`, ensures Python 3.11, installs deps.
2) Env vars:
   ```cmd
   copy config\example.env config\.env
   ```
   Set at least `DISCORD_BOT_TOKEN` (optional `DISCORD_BOT_PREFIX`, `FFMPEG_BINARY`).

## Run
- Using scripts:
  ```cmd
  start_bot.bat
  ```
  To stop: `stop_bot.bat`
- Or directly:
  ```cmd
  python -m src.bot.main
  ```

## Notes
This README stays minimal and is not updated on every feature change. Check `src/bot/commands/` for current command behavior. Contributions welcome.
