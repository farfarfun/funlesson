"""对 `claude` CLI 的单任务调用封装。

内容理解类工作（大纲结构化、PPT 文案、架构图代码）都通过这里的
`run_task` / `run_json_task` 调用一次性的 `claude -p` 完成，不接第三方 LLM API。
"""

import json
import re
import subprocess

DISALLOWED_TOOLS = "Bash Read Write Edit NotebookEdit WebFetch WebSearch Agent"


class AgentError(RuntimeError):
    pass


def run_task(prompt: str, *, timeout: int = 300) -> str:
    """执行一次 `claude -p` 单任务调用，返回模型的纯文本回复。"""
    cmd = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "text",
        "--disallowedTools",
        DISALLOWED_TOOLS,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as e:
        raise AgentError(
            "未找到 claude 命令，请确认 Claude Code CLI 已安装并在 PATH 中"
        ) from e
    except subprocess.TimeoutExpired as e:
        raise AgentError(f"claude 调用超时（{timeout}s）") from e

    if result.returncode != 0:
        raise AgentError(f"claude 调用失败: {result.stderr.strip()}")

    return result.stdout.strip()


def run_json_task(prompt: str, *, timeout: int = 300):
    """要求模型只输出 JSON 的单任务调用，做容错解析后返回 dict/list。"""
    text = run_task(prompt, timeout=timeout)
    return _extract_json(text)


def _extract_json(text: str):
    stripped = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.DOTALL)
    candidate = fence_match.group(1).strip() if fence_match else stripped
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise AgentError(
            f"无法解析 claude 返回的 JSON: {e}\n原始输出: {text[:500]}"
        ) from e
