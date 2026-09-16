# funlesson

funlesson 的核心处理库：把一条课程视频链接（B 站等）转成结构化图文教案素材——转写、大纲、思维导图、PPT、架构图。被
[funlesson-api](https://github.com/farfarfun/funlesson-api) 后端服务封装调用。

## 功能特性

- 视频下载：基于 `yt-dlp`，原生支持 B 站等多平台
- 语音转写：复用 [funtalk](https://github.com/farfarfun/funtalk) 的 Whisper 封装
- 大纲结构化 / PPT 文案 / 架构图代码：统一通过 `claude -p` 单任务调用完成内容理解，
  不依赖额外 LLM API Key（详见 `doc/API.md`）
- 思维导图：输出 markmap 兼容的 markdown 文本，交给前端渲染成可交互导图
- PPT：用 `python-pptx` 渲染成 `.pptx` 文件

## 快速开始

### 安装

```bash
uv pip install funlesson    # 或 pip install funlesson
```

从源码开发用可编辑模式：`pip install -e .`

### 环境要求

- 系统已安装 `ffmpeg`
- 本机已安装并登录 Claude Code CLI（`claude` 命令可用）
- 首次转写会下载 Whisper 模型权重，需要能访问模型源的网络环境

### 运行

```python
from funlesson import process

note = process("https://www.bilibili.com/video/BVxxxxxxxx", workdir="./data/demo")
print(note.outline.title)
print(note.mindmap)
```

## API 文档

见 [`doc/API.md`](doc/API.md)。

## 变更日志

见 [`CHANGELOG.md`](CHANGELOG.md)。

## 许可证

MIT
