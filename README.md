# OpenSource Discord Bot

Projeto aberto em Python com `discord.py`, organizado de forma modular para facilitar extensao e manutencao.

## Estrutura

- `src/bot/main.py`: inicia o bot, carrega extensoes e logging.
- `src/bot/commands/`: comandos desacoplados por arquivo (ex.: `ping`, `pingar`, `help`).
- `src/utils/`: utilidades compartilhadas (logging, FFmpeg loader, etc.).
- `config/example.env`: exemplo de variaveis; copie para `config/.env`.
- `requirements.txt`: dependencias.
- Scripts: `start_bot.bat` (abre console persistente) e `stop_bot.bat` (encerra instancia em execucao).

## Pre-requisitos

- Python 3.11+
- Criar um bot no Discord Developer Portal e obter `DISCORD_BOT_TOKEN`.
- FFmpeg disponivel ou configure `FFMPEG_BINARY` (Windows baixa automaticamente se nao houver).
- `PyNaCl` para voz (ja em `requirements.txt`).

## Configuracao

1) (Opcional) Ambiente virtual:

   ```python
   python -m venv .venv
   .venv\Scripts\activate
   ```

2) Variaveis: copie e edite

   ```cmd
   copy config\example.env config\.env
   ```

   Defina ao menos `DISCORD_BOT_TOKEN` e, opcionalmente, `DISCORD_BOT_PREFIX`.
3) Dependencias:

   ```python
   pip install -r requirements.txt
   ```

## Uso

- Rodar pelo script:

  ```exe
  start_bot.bat
  ```

  (para parar: `stop_bot.bat`)
- Ou diretamente:

  ```python
  python -m src.bot.main
  ```

## Observacao

Este README e enxuto e nao sera atualizado a cada mudanca de comando; consulte o codigo em `src/bot/commands/` para saber o comportamento atual. Contribuicoes sao bem-vindas.
