import logging
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from zipfile import ZipFile

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
CACHE_DIR = BASE_DIR / "config" / ".ffmpeg"
FFMPEG_TARGET = CACHE_DIR / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")

# Build Windows portavel (LGPL) de referencia
WIN_FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-lgpl.zip"
)


def _download_windows_ffmpeg() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp_path = Path(tmp.name)
    try:
        logger.info("Baixando FFmpeg portavel de %s ...", WIN_FFMPEG_URL)
        with urllib.request.urlopen(WIN_FFMPEG_URL, timeout=60) as response:
            with tmp_path.open("wb") as f:
                shutil.copyfileobj(response, f)

        with ZipFile(tmp_path, "r") as zip_file:
            member = next((m for m in zip_file.namelist() if m.endswith("ffmpeg.exe")), None)
            if not member:
                raise RuntimeError("Arquivo ffmpeg.exe nao encontrado no pacote baixado.")
            zip_file.extract(member, CACHE_DIR)
            extracted_path = CACHE_DIR / member
            extracted_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(extracted_path), FFMPEG_TARGET)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:  # pragma: no cover - limpeza best-effort
            pass

    return FFMPEG_TARGET


def ensure_ffmpeg_binary() -> str:
    """Resolve o caminho do FFmpeg, baixando automaticamente em Windows se necessario."""
    env_override = os.getenv("FFMPEG_BINARY")
    if env_override:
        logger.info("Usando FFmpeg definido em FFMPEG_BINARY: %s", env_override)
        return env_override

    if FFMPEG_TARGET.exists():
        resolved = str(FFMPEG_TARGET)
        logger.info("Usando FFmpeg em cache: %s", resolved)
        return resolved

    if os.name == "nt":
        downloaded = str(_download_windows_ffmpeg())
        logger.info("FFmpeg baixado para: %s", downloaded)
        return downloaded

    raise RuntimeError("FFmpeg nao encontrado. Defina FFMPEG_BINARY ou instale no sistema.")
