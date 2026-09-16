"""大纲转 markmap 兼容的 markdown 文本，交给前端渲染成可交互思维导图。"""

from .models import Outline, OutlineNode


def to_markmap(outline: Outline) -> str:
    lines = [f"# {outline.title}"]
    for node in outline.nodes:
        _render_node(node, level=1, lines=lines)
    return "\n".join(lines)


def _render_node(node: OutlineNode, level: int, lines: list[str]) -> None:
    indent = "  " * (level - 1)
    suffix = f"（{_format_ts(node.start)}）" if node.start is not None else ""
    lines.append(f"{indent}- {node.title}{suffix}")
    for child in node.children:
        _render_node(child, level + 1, lines)


def _format_ts(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
