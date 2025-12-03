import logging
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from zipfile import ZipFile

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "config" / ".ffmpeg"
FFMPEG_TARGET = CACHE_DIR / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")

# Fallback binario pre-compilado (Windows 64-bit). Outros SOs devem definir FFMPEG_BINARY manualmente.
WIN_FFMPEG_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-lgpl.zip"
)


def _download_windows_ffmpeg() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp_path = Path(tmp.name)
    try:
        logger.info("Baixando FFmpeg portavel de %s ...", WIN_FFMPEG_URL)
        urllib.request.urlretrieve(WIN_FFMPEG_URL, tmp_path)  # nosec - URL controlada conhecida

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
    """Resolve o caminho para o binario do FFmpeg, baixando automaticamente em Windows se necessario."""
    env_override = os.getenv("FFMPEG_BINARY")
    if env_override:
        return env_override

    if FFMPEG_TARGET.exists():
        return str(FFMPEG_TARGET)

    if os.name == "nt":
        return str(_download_windows_ffmpeg())

    raise RuntimeError(
        "FFmpeg nao encontrado. Defina FFMPEG_BINARY ou instale o binario para este sistema."
    )
