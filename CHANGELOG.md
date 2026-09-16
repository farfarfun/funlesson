# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/) 格式。

## [0.1.0] - 2026-09-16

### Added

- 核心处理管线 `funlesson_api.process`：课程视频链接 -> 下载音频（yt-dlp）
  -> 转写（复用 funtalk 的 Whisper 封装）-> 大纲结构化 -> 思维导图
  （markmap 文本）-> PPT（python-pptx）-> 架构图（Mermaid 文本）
- 内容理解相关步骤统一通过 `funlesson_api.agent` 调用一次性的 `claude -p` 任务
