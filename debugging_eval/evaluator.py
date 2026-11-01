"""Run strategies, score diagnoses, and export reproducible reports."""
from __future__ import annotations
import csv, json, math, statistics, time
from pathlib import Path
from typing import Any

def score_diagnosis(diagnosis: dict[str, Any], expected: str):
    label=str(diagnosis.get("root_cause","UNKNOWN")).upper().strip()
    actions=diagnosis.get("recommended_actions",[])
    complete=bool(label!="UNKNOWN" and diagnosis.get("explanation") and isinstance(actions,list) and len(actions)>0)
    return {"correct":label==expected,"complete":complete,"predicted_root_cause":label,"expected_root_cause":expected}

def run_evaluation(cases,strategies,repeats=1,model=None):
    results=[]
    for strategy in strategies:
        for case in cases:
            for run_index in range(1,repeats+1):
                started=time.perf_counter(); error=None
                try: diagnosis,usage=strategy.diagnose(case)
                except Exception as exc:
                    diagnosis={"root_cause":"UNKNOWN","explanation":"Strategy execution failed.","recommended_actions":[],"confidence":0.0,"parse_error":True}
                    usage={"prompt_tokens":0,"completion_tokens":0,"tool_calls":0}; error=f"{type(exc).__name__}: {exc}"
                latency=round((time.perf_counter()-started)*1000,2)
                scores=score_diagnosis(diagnosis,case["expected_root_cause"])
                results.append({"strategy":strategy.name,"case_id":case["case_id"],"category":case.get("category",case["expected_root_cause"]),"title":case["title"],"run":run_index,"latency_ms":latency,"prompt_tokens":usage.get("prompt_tokens",0),"completion_tokens":usage.get("completion_tokens",0),"estimated_tokens":usage.get("prompt_tokens",0)+usage.get("completion_tokens",0),"tool_calls":usage.get("tool_calls",0),"predicted_root_cause":scores["predicted_root_cause"],"expected_root_cause":scores["expected_root_cause"],"correct":scores["correct"],"complete":scores["complete"],"confidence":diagnosis.get("confidence",0.0),"explanation":diagnosis.get("explanation",""),"recommended_actions":diagnosis.get("recommended_actions",[]),"parse_error":bool(diagnosis.get("parse_error",False)),"error":error})
    return {"metadata":{"case_count":len(cases),"repeats":repeats,"model":model,"dataset":"15 balanced synthetic cases (3 per class)"},"results":results}

def _percentile(values, pct):
    if not values:return 0
    ordered=sorted(values); index=max(0,min(len(ordered)-1,math.ceil(pct*len(ordered))-1)); return round(ordered[index],2)

def summarize(report):
    grouped={}
    for row in report["results"]:grouped.setdefault(row["strategy"],[]).append(row)
    output=[]
    for name,rows in grouped.items():
        lat=[r["latency_ms"] for r in rows]; n=len(rows) or 1
        output.append({"strategy":name,"runs":len(rows),"accuracy_pct":round(100*sum(r["correct"] for r in rows)/n,2),"completeness_pct":round(100*sum(r["complete"] for r in rows)/n,2),"mean_latency_ms":round(statistics.mean(lat),2) if lat else 0,"median_latency_ms":round(statistics.median(lat),2) if lat else 0,"p95_latency_ms":_percentile(lat,.95),"mean_estimated_tokens":round(statistics.mean([r["estimated_tokens"] for r in rows]),2) if rows else 0,"tool_calls":sum(r["tool_calls"] for r in rows),"parse_failures":sum(r["parse_error"] for r in rows),"failures":sum(bool(r["error"]) for r in rows)})
    return output

def export_report(report,output_dir="reports"):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/"latest.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    cols=["strategy","case_id","category","title","run","latency_ms","prompt_tokens","completion_tokens","estimated_tokens","tool_calls","predicted_root_cause","expected_root_cause","correct","complete","confidence","parse_error","error"]
    with (out/"latest.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(report["results"])
    lines=["# Evaluation summary","",f"Cases: {report['metadata']['case_count']} | Repeats: {report['metadata']['repeats']} | Model: {report['metadata'].get('model')}","","| Strategy | Runs | Accuracy | Completeness | Mean ms | Median ms | P95 ms | Mean tokens | Tool calls | Failures | Parse errors |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summarize(report):lines.append(f"| {s['strategy']} | {s['runs']} | {s['accuracy_pct']}% | {s['completeness_pct']}% | {s['mean_latency_ms']} | {s['median_latency_ms']} | {s['p95_latency_ms']} | {s['mean_estimated_tokens']} | {s['tool_calls']} | {s['failures']} | {s['parse_failures']} |")
    lines += ["","## Interpretation notes","","- Exact-match accuracy is measured against the synthetic case label; it is not a measure of real-world debugging ability.","- Token counts are Ollama-reported prompt/completion counters; zero can mean the runtime did not provide a counter.","- Local inference cost is not monetized. Hardware and electricity costs are excluded.","- Review per-case output in `latest.csv` and `latest.json`; do not report only aggregate metrics.",""]
    (out/"summary.md").write_text("\n".join(lines),encoding="utf-8")
