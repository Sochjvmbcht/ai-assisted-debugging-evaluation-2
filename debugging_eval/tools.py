"""Read-only tools available to the tool-assisted debugging strategy."""
from __future__ import annotations
from typing import Any

def get_error_summary(case: dict[str, Any]) -> dict[str, Any]:
    """Return error-level lines and a small metadata summary."""
    lines = case["logs"].splitlines()
    errors = [line for line in lines if any(tag in line.upper() for tag in ("ERROR", "FATAL", "EXCEPTION"))]
    return {
        "case_id": case["case_id"],
        "error_count": len(errors),
        "error_lines": errors[:12],
        "total_log_lines": len(lines),
    }

def search_log(case: dict[str, Any], term: str) -> dict[str, Any]:
    """Search the supplied log text for a case-insensitive term."""
    if not isinstance(term, str) or not term.strip():
        return {"matches": [], "count": 0, "message": "Search term must be non-empty."}
    matches = [
        {"line_number": i, "text": line}
        for i, line in enumerate(case["logs"].splitlines(), start=1)
        if term.casefold() in line.casefold()
    ]
    return {"matches": matches[:20], "count": len(matches)}

def inspect_stack_trace(case: dict[str, Any]) -> dict[str, Any]:
    """Return stack-like lines without executing or opening anything."""
    lines = case["logs"].splitlines()
    stack = [
        {"line_number": i, "text": line}
        for i, line in enumerate(lines, start=1)
        if " at " in line or line.lstrip().startswith(("File ", "Traceback", "  "))
    ]
    return {"stack_trace": stack[:30], "count": len(stack)}

TOOL_FUNCTIONS = {
    "get_error_summary": get_error_summary,
    "search_log": search_log,
    "inspect_stack_trace": inspect_stack_trace,
}

OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_error_summary",
            "description": "Summarize error and fatal log lines from the supplied case.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_log",
            "description": "Search the supplied log for a keyword such as timeout, database, memory, or connection.",
            "parameters": {
                "type": "object",
                "properties": {"term": {"type": "string", "description": "Case-insensitive search term"}},
                "required": ["term"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_stack_trace",
            "description": "Inspect stack-trace-like lines in the supplied log.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

def execute_tool(name: str, arguments: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """Dispatch only allow-listed, read-only tools."""
    if name not in TOOL_FUNCTIONS:
        return {"error": f"Tool '{name}' is not available."}
    try:
        if name == "search_log":
            return TOOL_FUNCTIONS[name](case, str(arguments.get("term", "")))
        return TOOL_FUNCTIONS[name](case)
    except Exception as exc:  # defensive boundary around model-provided arguments
        return {"error": f"Tool execution failed: {type(exc).__name__}"}
