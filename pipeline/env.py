"""
Кросс-платформенный резолвер ffmpeg (Windows/macOS/Linux).
Порядок: env FFMPEG -> системный ffmpeg в PATH -> бинарь из пакета imageio-ffmpeg.
"""
import os, shutil
def ffmpeg_exe():
    p=os.environ.get("FFMPEG")
    if p and os.path.exists(p): return p
    p=shutil.which("ffmpeg")
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"  # последняя надежда
FFMPEG=ffmpeg_exe()
