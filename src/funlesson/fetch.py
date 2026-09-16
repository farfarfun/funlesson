"""课程视频下载，基于 yt-dlp（原生支持 B 站、抖音等多平台）。"""

import http.client
import os
from urllib.parse import urlsplit

from .models import MediaInfo

_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
_REDIRECT_CODES = {301, 302, 303, 307, 308}
_MAX_HOPS = 5


def _resolve_redirects(url: str) -> str:
    """跟随重定向拿到最终链接。

    yt-dlp 没有 b23.tv 之类短链的专用 extractor，只能落到 generic extractor 直接抓
    网页，而 bilibili 对短链请求头稍微复杂一点（比如 urllib.request 默认加的那些
    header）就会返回 412，所以这里手写一个只带最基本 header 的 HEAD 请求来解析重
    定向，而不是走 urllib 的 opener。分享出来的课程链接十有八九是短链，下载前先自
    己解析一遍，把最终的 bilibili.com/... 链接交给 yt-dlp。
    """
    current = url
    for _ in range(_MAX_HOPS):
        parts = urlsplit(current)
        if parts.scheme not in ("http", "https"):
            return url
        conn_cls = (
            http.client.HTTPSConnection
            if parts.scheme == "https"
            else http.client.HTTPConnection
        )
        try:
            conn = conn_cls(parts.netloc, timeout=10)
            path = parts.path or "/"
            if parts.query:
                path += "?" + parts.query
            conn.request("HEAD", path, headers={"User-Agent": _UA, "Accept": "*/*"})
            resp = conn.getresponse()
            resp.read()
            conn.close()
        except Exception:
            return url

        if resp.status not in _REDIRECT_CODES:
            return current
        location = resp.getheader("Location")
        if not location:
            return current
        current = (
            location
            if urlsplit(location).netloc
            else f"{parts.scheme}://{parts.netloc}{location}"
        )

    return current


def download(url: str, out_dir: str) -> MediaInfo:
    import yt_dlp

    url = _resolve_redirects(url)
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
