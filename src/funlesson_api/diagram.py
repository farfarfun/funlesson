"""从大纲/转写文本中提炼可视化的流程、架构等内容，生成 Mermaid 图代码。"""

from . import agent
from .models import DiagramSpec, Outline, Transcript

_PROMPT_TEMPLATE = """你是一名教学助理，请阅读下面课程的大纲标题和转写全文，判断内容里是否包含适合画成图的流程、架构、步骤或分类关系。

要求：
- 如果没有适合画图的内容，输出 {{"diagrams": []}}
- 如果有，为每个值得画图的部分生成一段 Mermaid 图代码（flowchart/sequenceDiagram/classDiagram 等，自行选择合适类型），最多 3 个
- 只输出 JSON，不要输出任何解释性文字，格式：{{"diagrams": [{{"title": "...", "mermaid": "flowchart TD\\n  A --> B"}}]}}

课程大纲标题：{outline_title}

转写全文（节选，可能被截断）：
{full_text}
"""


def build_diagrams(outline: Outline, transcript: Transcript) -> list[DiagramSpec]:
    full_text = transcript.full_text[:6000]
    prompt = _PROMPT_TEMPLATE.format(outline_title=outline.title, full_text=full_text)
    data = agent.run_json_task(prompt, timeout=600)
    return [
        DiagramSpec(title=d.get("title", ""), mermaid=d.get("mermaid", ""))
        for d in data.get("diagrams", [])
    ]
