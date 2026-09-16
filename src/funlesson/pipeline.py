"""串联下载 -> 转写 -> 大纲 -> 思维导图/PPT/架构图 的完整处理流程。"""

import os
from typing import Callable, Optional

from . import asr as asr_mod
from . import diagram as diagram_mod
from . import fetch as fetch_mod
from . import mindmap as mindmap_mod
from . import outline as outline_mod
from . import ppt as ppt_mod
from .models import Note

ProgressCallback = Optional[Callable[[str, Optional[float]], None]]

STEPS = ["fetch", "asr", "outline", "mindmap", "ppt", "diagram"]


def process(url: str, workdir: str, on_progress: ProgressCallback = None) -> Note:
    def report(step: str, percent: Optional[float] = None) -> None:
        if on_progress:
            on_progress(step, percent)

    os.makedirs(workdir, exist_ok=True)

    report("fetch")
    media = fetch_mod.download(url, workdir)

    report("asr")
    transcript = asr_mod.transcribe(
        media.audio_path, on_progress=lambda p: report("asr", p)
    )

    report("outline")
    outline = outline_mod.build_outline(transcript)

    report("mindmap")
    mindmap = mindmap_mod.to_markmap(outline)

    report("ppt")
    ppt_path = ppt_mod.build_ppt(outline, os.path.join(workdir, "slides.pptx"))

    report("diagram")
    diagrams = diagram_mod.build_diagrams(outline, transcript)

    return Note(
        media=media,
        transcript=transcript,
        outline=outline,
        mindmap=mindmap,
        diagrams=diagrams,
        ppt_path=ppt_path,
    )
