from funlesson.mindmap import to_markmap
from funlesson.models import Outline, OutlineNode
from funlesson.outline import _parse_outline


def _sample_outline() -> Outline:
    return Outline(
        title="课程标题",
        nodes=[
            OutlineNode(
                title="第一章",
                start=0.0,
                children=[OutlineNode(title="第一节", start=12.5, children=[])],
            ),
            OutlineNode(title="第二章", start=90.0, children=[]),
        ],
    )


def test_parse_outline_builds_tree_from_dict():
    data = {
        "title": "课程标题",
        "nodes": [
            {
                "title": "第一章",
                "start": 0.0,
                "children": [{"title": "第一节", "start": 12.5, "children": []}],
            },
            {"title": "第二章", "start": 90.0, "children": []},
        ],
    }

    outline = _parse_outline(data)

    assert outline.title == "课程标题"
    assert outline.nodes[0].children[0].title == "第一节"
    assert outline.nodes[1].start == 90.0


def test_parse_outline_handles_missing_fields():
    outline = _parse_outline({})

    assert outline.title == ""
    assert outline.nodes == []


def test_to_markmap_renders_nested_bullets_with_timestamps():
    text = to_markmap(_sample_outline())

    lines = text.splitlines()
    assert lines[0] == "# 课程标题"
    assert lines[1] == "- 第一章（00:00）"
    assert lines[2] == "  - 第一节（00:12）"
    assert lines[3] == "- 第二章（01:30）"
