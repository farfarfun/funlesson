"""验证 on_progress 回调在 asr.py 和 pipeline.py 里被正确透传。

funtalk 自己的测试套件已经用真实 tiny 模型验证过 whisper 逐帧进度的机制本身
（frame-level tqdm 更新、单调递增到 1.0），这里只测本仓库新写的两层胶水代码：
asr.transcribe() 是否把 on_progress 原样转发给 funtalk 的 WhisperASR.transcribe，
以及 pipeline.process() 的 asr 步骤是否把每次百分比回调正确转成
on_progress("asr", percent) 传给调用方。因此在 funtalk 边界打桩（和 funtalk
自己测试 whisper 边界的方式一致），而不是重新跑一次真实模型推理。
"""

from unittest.mock import MagicMock

import funlesson.asr as asr_mod
import funlesson.pipeline as pipeline_mod
from funlesson.models import MediaInfo, Outline, Transcript


def test_asr_transcribe_forwards_on_progress(monkeypatch):
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {
        "text": "你好世界",
        "segments": [{"start": 0.0, "end": 1.0, "text": "你好世界"}],
    }
    monkeypatch.setattr(asr_mod, "_get_model", lambda name="turbo": fake_model)

    received = []
    transcript = asr_mod.transcribe("audio.wav", on_progress=received.append)

    fake_model.transcribe.assert_called_once_with(
        "audio.wav", language="ZH", on_progress=received.append
    )
    assert transcript.full_text == "你好世界"
    assert transcript.segments[0].text == "你好世界"


def test_asr_transcribe_works_without_on_progress(monkeypatch):
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {"text": "hi", "segments": []}
    monkeypatch.setattr(asr_mod, "_get_model", lambda name="turbo": fake_model)

    transcript = asr_mod.transcribe("audio.wav")

    fake_model.transcribe.assert_called_once_with(
        "audio.wav", language="ZH", on_progress=None
    )
    assert transcript.full_text == "hi"


def test_pipeline_process_threads_asr_percent_through_on_progress(
    monkeypatch, tmp_path
):
    media = MediaInfo(
        url="http://x", title="t", duration=1.0, cover=None, audio_path="a.wav"
    )
    transcript = Transcript(full_text="hi", segments=[])
    outline = Outline(title="t", nodes=[])

    monkeypatch.setattr(pipeline_mod.fetch_mod, "download", lambda url, workdir: media)
    monkeypatch.setattr(pipeline_mod.outline_mod, "build_outline", lambda t: outline)
    monkeypatch.setattr(pipeline_mod.mindmap_mod, "to_markmap", lambda o: "# t")
    monkeypatch.setattr(pipeline_mod.ppt_mod, "build_ppt", lambda o, path: path)
    monkeypatch.setattr(pipeline_mod.diagram_mod, "build_diagrams", lambda o, t: [])

    def fake_transcribe(
        audio_path, *, language="ZH", model_name="turbo", on_progress=None
    ):
        assert on_progress is not None, (
            "pipeline 没有把 on_progress 传给 asr_mod.transcribe"
        )
        on_progress(0.0)
        on_progress(0.5)
        on_progress(1.0)
        return transcript

    monkeypatch.setattr(pipeline_mod.asr_mod, "transcribe", fake_transcribe)

    calls = []
    pipeline_mod.process(
        "http://x",
        str(tmp_path),
        on_progress=lambda step, pct: calls.append((step, pct)),
    )

    assert ("fetch", None) in calls
    assert ("asr", 0.0) in calls
    assert ("asr", 0.5) in calls
    assert ("asr", 1.0) in calls
    assert ("outline", None) in calls
    assert ("mindmap", None) in calls
    assert ("ppt", None) in calls
    assert ("diagram", None) in calls
    # asr 的百分比必须紧跟在 "asr" 步骤边界之后，且早于 outline
    assert ("asr", None) in calls
    assert calls.index(("asr", None)) < calls.index(("outline", None))
