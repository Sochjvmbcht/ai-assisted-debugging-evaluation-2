"""Prompt templates and robust diagnosis parsing."""
from __future__ import annotations
import json
from typing import Any

LABELS = ["DATABASE_CONNECTION_POOL_EXHAUSTED", "NETWORK_TIMEOUT", "NULL_REFERENCE", "OUT_OF_MEMORY", "AUTHENTICATION_FAILURE", "UNKNOWN"]
SYSTEM_PROMPT = f"""You are a cautious software incident triage engineer. Diagnose only from the evidence provided.
Choose exactly one root_cause label from: {', '.join(LABELS)}.
Distinguish the primary failure from downstream symptoms. For example, a timeout while acquiring a DB connection is pool exhaustion; a read/DNS/socket timeout is a network timeout; null/None dereference is NULL_REFERENCE; MemoryError, heap-space, or OOMKilled is OUT_OF_MEMORY; HTTP 401, expired credentials, invalid key or JWT signature is AUTHENTICATION_FAILURE.
Do not invent infrastructure facts. Cite concrete log fragments in explanation. Recommend two safe investigation/remediation actions.
Return one JSON object only with keys root_cause, explanation, recommended_actions (array of strings), confidence (number 0..1)."""

def _evidence_lines(logs: str) -> list[str]:
    markers = ("ERROR", "FATAL", "EXCEPTION", "WARN", "401", "OOM", "timeout", "pool", "null", "memory", "credential", "signature")
    selected = [line for line in logs.splitlines() if any(m.casefold() in line.casefold() for m in markers)]
    return selected[:12]

def structured_messages(case: dict[str, Any]) -> list[dict[str, str]]:
    context = {"case_id": case["case_id"], "title": case["title"], "evidence_lines": _evidence_lines(case["logs"]), "full_log": case["logs"]}
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Diagnose this log case. Return JSON only.\n" + json.dumps(context, indent=2)}]

def tool_messages(case: dict[str, Any]) -> list[dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT + "\nYou may call at most one read-only inspection tool if it adds evidence. Then provide the final JSON diagnosis."}, {"role": "user", "content": f"Case {case['case_id']} — {case['title']}\nRaw logs:\n{case['logs']}\nInspect relevant evidence if useful, then diagnose."}]

def parse_diagnosis(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return {"root_cause":"UNKNOWN", "explanation":f"No JSON object in response: {content[:300]}", "recommended_actions":[], "confidence":0.0, "parse_error":True}
    try:
        result = json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return {"root_cause":"UNKNOWN", "explanation":f"Malformed JSON: {content[:300]}", "recommended_actions":[], "confidence":0.0, "parse_error":True}
    if not isinstance(result, dict):
        return {"root_cause":"UNKNOWN", "explanation":"JSON response was not an object.", "recommended_actions":[], "confidence":0.0, "parse_error":True}
    label = str(result.get("root_cause", "UNKNOWN")).upper().strip()
    if label not in LABELS:
        label = "UNKNOWN"
    actions = result.get("recommended_actions", [])
    if not isinstance(actions, list): actions = [str(actions)]
    try: confidence = float(result.get("confidence", 0.0))
    except (TypeError, ValueError): confidence = 0.0
    return {"root_cause":label, "explanation":str(result.get("explanation", "")), "recommended_actions":[str(x) for x in actions if str(x).strip()], "confidence":max(0.0,min(1.0,confidence))}
