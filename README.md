# Bot do Discord

Base inicial em Python usando `discord.py`, com comandos separados por arquivo em `src/bot/commands` (um comando `ping` ja incluido).

## Estrutura
- `src/bot/main.py`: ponto de entrada que carrega comandos e inicia o bot.
- `src/bot/commands/`: um arquivo por comando (`ping.py`).
- `src/utils/`: utilitarios compartilhados (ex: audio e busca).
- `config/example.env`: exemplo de variaveis de ambiente.
- `requirements.txt`: dependencias do projeto.
- `.gitattributes` e `.gitignore`: configuracoes de git.

## Requisitos
- Python 3.11+
- Token do bot no Portal de Desenvolvedores do Discord (habilite a intent de message content para comandos prefixados).
- FFmpeg para tocar audio (pode estar no PATH ou apontado pela variavel `FFMPEG_BINARY`; em Windows o bot baixa automaticamente um binario portavel se nao houver).
- Dependencia de voz `PyNaCl` (incluida em `requirements.txt`).

## Como comecar
1) Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate  # Windows
   # ou
   source .venv/bin/activate  # Linux/macOS
   ```
2) Copie o exemplo de variaveis:
   ```bash
   copy config\\example.env config\\.env  # Windows
   # ou
   cp config/example.env config/.env        # Linux/macOS
   ```
3) Instale dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   - Se nao quiser instalar o FFmpeg no PATH, defina `FFMPEG_BINARY` com o caminho completo do executavel (ex: `FFMPEG_BINARY=bin/ffmpeg.exe`). Em Windows, sem essa variavel, o bot baixa automaticamente um pacote portavel (BtbN/FFmpeg-Builds) para `config/.ffmpeg/`.
4) Execute o bot (no diretorio raiz do projeto):
   ```bash
   python -m src.bot.main
   ```

## Uso inicial
- Defina `DISCORD_BOT_TOKEN` e, opcionalmente, ajuste `DISCORD_BOT_PREFIX` no arquivo `.env` (padrao `s!`).
- Comando `!ping` (ou usando o prefixo configurado): responde com a latencia atual do bot.
- Comando `!play {busca}`: entra no seu canal de voz e toca o melhor resultado na ordem YouTube > Spotify > SoundCloud > Deezer.
- Para criar novos comandos, adicione um novo arquivo `.py` em `src/bot/commands` contendo uma `Cog` e uma funcao `async def setup(bot)` para registrar o comando.

## Proximos passos sugeridos
- Adicionar logs estruturados e tratamento de erros ao inicializar o bot.
- Criar comandos adicionais (por exemplo, `!help` customizado ou comandos de moderacao).
- Configurar pipeline de testes/CI para checar estilo e lint.
