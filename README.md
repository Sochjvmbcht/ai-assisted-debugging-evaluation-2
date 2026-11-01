# AI-Assisted Debugging Evaluation Framework

A reproducible Python portfolio project comparing three approaches to diagnosing **synthetic application logs**:

1. **Structured-context LLM** — Python extracts likely evidence and sends a structured log bundle to a local LLM.
2. **Tool-assisted LLM** — the LLM can call one bounded, read-only Python inspection tool, then must return a final diagnosis.
3. **Rule-based baseline** — transparent keyword rules provide a non-LLM reference point.

The dataset contains 15 synthetic cases balanced across five root-cause classes (three cases per class). The evaluator reports exact-match accuracy, completeness, mean/median/p95 latency, Ollama token counters, tool calls, parse failures, and execution failures.

> Educational simulation only. It is not connected to Apple systems, cellular baseband firmware, real device coredumps, or production debugging infrastructure.

## Requirements
- Python 3.10+
- Ollama installed and running
- Recommended model for this project: `llama3.2:3b` (may be slow or memory-constrained on 8 GB machines; `llama3.2:1b` remains available for comparison)
- Python standard library only

## Quick start (macOS)
```bash
ollama pull llama3.2:3b
# Ollama normally runs as a background app; if not, start it in a separate terminal:
ollama serve
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m debugging_eval --strategy all --model llama3.2:3b --timeout 60
```

To use the smaller model on a memory-constrained machine:
```bash
python -m debugging_eval --strategy all --model llama3.2:1b --timeout 60
```

Run each strategy twice per case (slower):
```bash
python -m debugging_eval --strategy all --model llama3.2:3b --repeats 2
```

Run only the no-LLM baseline without Ollama:
```bash
python -m debugging_eval --strategy rule_based
```

The tool-assisted strategy is deliberately bounded to one tool call by default. Use `--max-tool-calls 0` to disable tool calls or `2` to allow up to two. Each Ollama request has a 60-second default timeout. The final tool-assisted turn disables tools so the model must provide a diagnosis instead of looping.

## Outputs
- `reports/latest.json` — per-case diagnoses and run metadata
- `reports/latest.csv` — analysis-friendly rows
- `reports/summary.md` — comparison summary

## Evaluation definitions
- **Accuracy:** exact match between normalized predicted label and expected synthetic label.
- **Completeness:** non-UNKNOWN root cause, non-empty explanation, and at least one recommended action.
- **Latency:** wall-clock time for the strategy, including tool calls.
- **Tokens:** prompt and completion counts returned by Ollama.
- **P95:** nearest-rank 95th percentile of observed run latencies.
- **Rule baseline:** simple keyword matching; transparent and intentionally not an ML model.

## Project structure
```text
ai-assisted-debugging-evaluation/
├── debugging_eval/  # CLI, Ollama client, prompts, strategies, evaluator
├── data/            # 15 balanced synthetic log cases
├── reports/         # generated JSON, CSV and Markdown reports
└── tests/           # offline unit tests
```

## Limitations and responsible reporting
- Logs are synthetic; results cannot be generalized to production debugging or baseband systems.
- The dataset is small and hand-authored. Treat results as a portfolio experiment, not a benchmark.
- A keyword baseline can match obvious patterns and is not equivalent to a production diagnostic engine.
- LLM accuracy must be judged from actual runs. Do not claim a target accuracy or copy unexecuted metrics into a CV.
- The tools only inspect the supplied in-memory log text. They do not execute shell commands or access real devices.

## CV wording (only after implementation and testing)
**AI-Assisted Debugging Evaluation Framework | Python, Ollama, LLM Tool Calling**
- Developed a Python evaluation harness comparing structured-context and bounded tool-assisted LLM workflows against a transparent rule-based baseline on 15 synthetic debugging cases.
- Implemented read-only log inspection tools and automated reporting for root-cause accuracy, response latency, token usage, and output completeness.
- Generated reproducible JSON/CSV evaluation reports and analyzed per-case failures across five error categories.
