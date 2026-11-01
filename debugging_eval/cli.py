"""Command-line entry point."""
from __future__ import annotations
import argparse
from .dataset import load_cases
from .evaluator import export_report, summarize, run_evaluation
from .ollama_client import OllamaClient
from .strategies import StructuredStrategy, ToolAssistedStrategy, RuleBasedStrategy

def build_parser():
    p=argparse.ArgumentParser(description="Compare local LLM debugging strategies on synthetic logs.")
    p.add_argument("--strategy",choices=["structured","tool_assisted","rule_based","both","all"],default="all")
    p.add_argument("--model",default="llama3.2:3b")
    p.add_argument("--base-url",default="http://localhost:11434")
    p.add_argument("--timeout",type=int,default=60,help="Per Ollama request timeout in seconds")
    p.add_argument("--repeats",type=int,default=1)
    p.add_argument("--output-dir",default="reports")
    p.add_argument("--max-tool-calls",type=int,default=1)
    return p

def main():
    args=build_parser().parse_args()
    if args.repeats<1: raise SystemExit("--repeats must be at least 1")
    if args.timeout<1: raise SystemExit("--timeout must be positive")
    if args.max_tool_calls not in (0,1,2): raise SystemExit("--max-tool-calls must be 0, 1, or 2")
    cases=load_cases()
    rules=RuleBasedStrategy()
    if args.strategy=="rule_based": strategies=[rules]
    else:
        client=OllamaClient(args.base_url,args.model,args.timeout)
        client.ensure_model()
        available={"structured":StructuredStrategy(client),"tool_assisted":ToolAssistedStrategy(client,args.max_tool_calls),"rule_based":rules}
        strategies=list(available.values()) if args.strategy in ("all","both") else [available[args.strategy]]
    print(f"Evaluating {len(cases)} synthetic cases with {args.model if args.strategy!='rule_based' else 'keyword baseline'}...")
    report=run_evaluation(cases,strategies,repeats=args.repeats,model=args.model)
    export_report(report,args.output_dir)
    print("\nResults:")
    for row in summarize(report):
        print(f"- {row['strategy']}: accuracy={row['accuracy_pct']}%, completeness={row['completeness_pct']}%, mean latency={row['mean_latency_ms']} ms, median={row['median_latency_ms']} ms, p95={row['p95_latency_ms']} ms, failures={row['failures']}, mean tokens={row['mean_estimated_tokens']}")
    print(f"\nReports saved to: {args.output_dir}/")
if __name__=="__main__": main()
