from dataclasses import dataclass, field


@dataclass
class MediaInfo:
    url: str
    title: str
    duration: float | None
    cover: str | None
    audio_path: str


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    full_text: str
    segments: list[TranscriptSegment] = field(default_factory=list)


@dataclass
class OutlineNode:
    title: str
    start: float | None = None
    children: list["OutlineNode"] = field(default_factory=list)


@dataclass
class Outline:
    title: str
    nodes: list[OutlineNode] = field(default_factory=list)


@dataclass
class DiagramSpec:
    title: str
    mermaid: str


@dataclass
class Note:
    media: MediaInfo
    transcript: Transcript
    outline: Outline
    mindmap: str
    diagrams: list[DiagramSpec]
    ppt_path: str
