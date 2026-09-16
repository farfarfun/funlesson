"""课程视频下载，基于 yt-dlp（原生支持 B 站、抖音等多平台）。"""

import os

from .models import MediaInfo


def download(url: str, out_dir: str) -> MediaInfo:
    import yt_dlp

    os.makedirs(out_dir, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "audio.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    audio_path = os.path.join(out_dir, "audio.mp3")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"下载完成但未找到音频文件: {audio_path}")

    return MediaInfo(
        url=url,
        title=info.get("title") or url,
        duration=info.get("duration"),
        cover=info.get("thumbnail"),
        audio_path=audio_path,
    )
