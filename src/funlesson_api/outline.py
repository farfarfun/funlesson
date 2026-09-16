"""把转写文字稿结构化为大纲，由 claude 单任务调用完成理解。"""

from . import agent
from .models import Outline, OutlineNode, Transcript

_PROMPT_TEMPLATE = """你是一名教学助理，请阅读下面这段课程视频的转写文字稿，将内容整理成结构化大纲。

要求：
- 大纲是一个多级标题树，覆盖视频的主要知识点，层级不超过 3 层
- 每个大纲节点都要尽量给出这段内容在原文中对应的起始时间（秒），从下面提供的分段时间戳里估算，找不到就填 null
- 只输出 JSON，不要输出任何解释性文字，格式如下：
{{"title": "整体标题", "nodes": [{{"title": "一级标题", "start": 12.5, "children": [{{"title": "二级标题", "start": 30.0, "children": []}}]}}]}}

转写分段（每行是 [起始秒] 文本）：
{segments}
"""


def build_outline(transcript: Transcript) -> Outline:
    segments_text = "\n".join(
        f"[{seg.start:.1f}] {seg.text}" for seg in transcript.segments
    )
    prompt = _PROMPT_TEMPLATE.format(segments=segments_text)
    data = agent.run_json_task(prompt, timeout=600)
    return _parse_outline(data)


def _parse_outline(data: dict) -> Outline:
    def parse_node(n: dict) -> OutlineNode:
        return OutlineNode(
            title=n.get("title", ""),
            start=n.get("start"),
            children=[parse_node(c) for c in n.get("children", [])],
        )

    return Outline(
        title=data.get("title", ""),
        nodes=[parse_node(n) for n in data.get("nodes", [])],
    )
