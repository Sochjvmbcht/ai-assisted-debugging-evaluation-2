"""LLM and transparent rule-based debugging strategies."""
from __future__ import annotations
import json
from typing import Any
from .ollama_client import OllamaClient
from .prompts import structured_messages, tool_messages, parse_diagnosis
from .tools import OLLAMA_TOOLS, execute_tool

class StructuredStrategy:
    name = "structured"
    def __init__(self, client: OllamaClient): self.client = client
    def diagnose(self, case: dict[str, Any]):
        response = self.client.chat(structured_messages(case), json_mode=True)
        usage = {"prompt_tokens":int(response.get("prompt_eval_count",0) or 0),"completion_tokens":int(response.get("eval_count",0) or 0),"tool_calls":0}
        return parse_diagnosis(response.get("message",{}).get("content","")), usage

class ToolAssistedStrategy:
    name = "tool_assisted"
    def __init__(self, client: OllamaClient, max_tool_calls: int = 1):
        self.client, self.max_tool_calls = client, max(0, min(2, max_tool_calls))
    def diagnose(self, case: dict[str, Any]):
        messages = tool_messages(case)
        prompt_tokens = completion_tokens = tool_count = 0
        response = self.client.chat(messages, tools=OLLAMA_TOOLS)
        prompt_tokens += int(response.get("prompt_eval_count",0) or 0)
        completion_tokens += int(response.get("eval_count",0) or 0)
        message = response.get("message", {})
        calls = (message.get("tool_calls") or [])[:self.max_tool_calls]
        if calls:
            messages.append(message)
            for call in calls:
                fn = call.get("function", {})
                name, args = fn.get("name", ""), fn.get("arguments", {})
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except json.JSONDecodeError: args = {}
                result = execute_tool(name, args if isinstance(args,dict) else {}, case)
                messages.append({"role":"tool", "name":name, "content":json.dumps(result)})
                tool_count += 1
            # Crucial: disable tools on the final turn, so the model must return a diagnosis.
            messages.append({"role":"user", "content":"You have the inspection result. Do not call more tools. Return the final diagnosis as JSON only."})
            final = self.client.chat(messages, json_mode=True)
            prompt_tokens += int(final.get("prompt_eval_count",0) or 0)
            completion_tokens += int(final.get("eval_count",0) or 0)
            message = final.get("message", {})
        elif message.get("content", "").strip():
            # Some models choose not to call a tool; use their direct answer.
            pass
        diagnosis = parse_diagnosis(message.get("content", ""))
        return diagnosis, {"prompt_tokens":prompt_tokens,"completion_tokens":completion_tokens,"tool_calls":tool_count}

class RuleBasedStrategy:
    """Transparent keyword baseline; included as a non-LLM reference point."""
    name = "rule_based"
    RULES = [
        ("DATABASE_CONNECTION_POOL_EXHAUSTED", ("pool exhausted", "no database connection", "db_pool", "poolacquiretimeout", "waiting_for_database_connection")),
        ("NETWORK_TIMEOUT", ("readtimeout", "socket.timeout", "dns lookup timed out", "connection reset", "upstream request timed out")),
        ("NULL_REFERENCE", ("nonetype", "nullreferenceexception", "cannot read property", "object reference not set")),
        ("OUT_OF_MEMORY", ("outofmemory", "memoryerror", "oomkilled", "heap space", "unable to allocate")),
        ("AUTHENTICATION_FAILURE", ("status=401", "expired access token", "invalid api key", "invalidsignatureerror", "signature verification failed")),
    ]
    def diagnose(self, case: dict[str, Any]):
        logs = case["logs"].casefold()
        scores = [(sum(logs.count(term) for term in terms), label) for label, terms in self.RULES]
        score, label = max(scores)
        if score == 0: label = "UNKNOWN"
        return {"root_cause":label,"explanation":f"Keyword baseline matched {score} indicator(s) for {label}.","recommended_actions":["Inspect the matching log evidence.","Verify the suspected subsystem with a targeted diagnostic."],"confidence":0.5 if score else 0.0}, {"prompt_tokens":0,"completion_tokens":0,"tool_calls":0}
