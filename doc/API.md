# API 文档

## `funlesson.process(url, workdir, on_progress=None) -> Note`

课程视频链接 -> 图文笔记全流程处理入口。

- `url`：课程视频链接（B 站等 yt-dlp 支持的平台）
- `workdir`：处理过程产物落盘目录（音频、`slides.pptx` 等）
- `on_progress`：可选回调 `(step: str) -> None`，依次收到
  `"fetch" -> "asr" -> "outline" -> "mindmap" -> "ppt" -> "diagram"`，用于给上层任务系统更新进度

返回 `Note`：

```python
@dataclass
class Note:
    media: MediaInfo  # 视频信息：url/title/duration/cover/audio_path
    transcript: Transcript  # 转写：full_text + segments(start,end,text)
    outline: Outline  # 大纲：title + nodes(标题树，含 start 时间戳)
    mindmap: str  # markmap 兼容的 markdown 思维导图文本
    diagrams: list[DiagramSpec]  # 架构图，每个是 {title, mermaid}
    ppt_path: str  # 生成的 slides.pptx 路径
```

## 分步模块

各步骤也可单独调用，方便测试或替换实现：

- `funlesson.fetch.download(url, out_dir) -> MediaInfo`：yt-dlp 下载音频
- `funlesson.asr.transcribe(audio_path) -> Transcript`：基于 `funtalk.asr.WhisperASR`
- `funlesson.outline.build_outline(transcript) -> Outline`
- `funlesson.mindmap.to_markmap(outline) -> str`
- `funlesson.ppt.build_ppt(outline, out_path) -> str`
- `funlesson.diagram.build_diagrams(outline, transcript) -> list[DiagramSpec]`

## `funlesson.agent`

内容理解相关步骤（`outline`/`ppt`/`diagram`）统一通过这里调用一次性的
`claude -p` 任务，不依赖额外的 LLM API Key：

- `agent.run_task(prompt, timeout=300) -> str`：单任务调用，返回纯文本
- `agent.run_json_task(prompt, timeout=300) -> dict | list`：约定模型只输出 JSON，做容错解析

运行环境要求本机已安装并登录 Claude Code CLI（`claude` 命令可用）。

## 依赖与环境要求

- 系统需安装 `ffmpeg`（yt-dlp 音频提取、Whisper 转写都依赖它）
- `funlesson.asr` 首次调用会触发 Whisper 模型下载，网络環境需能访问模型权重源
