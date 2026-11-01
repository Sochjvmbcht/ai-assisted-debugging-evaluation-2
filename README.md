# AI-Assisted Debugging Evaluation Framework

A Python-based experimental framework for comparing different approaches to diagnosing synthetic application logs using local large language models (LLMs).

The project evaluates whether providing structured diagnostic context or allowing bounded tool-assisted investigation changes diagnostic accuracy, completeness, and execution performance.

## Overview

The framework compares three diagnostic strategies:

1. **Structured-context LLM** — Python extracts relevant evidence from the supplied logs and provides the LLM with a structured diagnostic context.
2. **Tool-assisted LLM** — The LLM can request information through a bounded, read-only Python inspection tool before producing its final diagnosis.
3. **Rule-based baseline** — Transparent keyword-matching rules provide a deterministic, non-LLM comparison.

The evaluation dataset contains **15 synthetic debugging cases**, balanced across five root-cause categories, with three cases per category.

The evaluator collects diagnostic results and performance measurements to support repeatable comparisons.

## Key Features

- Three interchangeable diagnostic strategies.
- Local LLM inference through Ollama.
- Bounded, read-only log inspection for tool-assisted diagnosis.
- Synthetic dataset with predefined expected root-cause labels.
- Exact-match diagnostic accuracy and output completeness evaluation.
- Mean, median, and p95 latency measurements.
- Ollama prompt and completion token counters.
- Tool-call, parsing-failure, and execution-failure tracking.
- JSON, CSV, and Markdown evaluation reports.
- Offline unit tests for core functionality.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.10+ |
| LLM runtime | Ollama |
| Evaluation model | Llama 3.2 (3B recommended) |
| Smaller model option | Llama 3.2 (1B) |
| Diagnostic approaches | LLM prompting, tool calling, keyword rules |
| Testing | Python unittest |
| Reporting | JSON, CSV, Markdown |

The implementation uses the Python standard library without additional Python package dependencies.

## Architecture

The evaluation process follows this general workflow:

1. Load a synthetic diagnostic case and its expected root-cause label.
2. Execute the selected diagnostic strategy.
3. Collect the predicted diagnosis, explanation, and recommended action.
4. Measure execution time and available model usage information.
5. Compare the predicted diagnosis with the expected label.
6. Store the results for analysis and reporting.

### Strategy comparison

| Strategy | Diagnostic approach | Purpose |
|---|---|---|
| Structured-context LLM | Pre-extracted evidence supplied to an LLM | Evaluate structured diagnostic context |
| Tool-assisted LLM | LLM investigates logs using a bounded inspection tool | Evaluate interactive evidence gathering |
| Rule-based baseline | Keyword-based diagnostic rules | Establish a deterministic reference |

## Requirements

- Python 3.10 or newer
- Ollama installed and running
- Llama 3.2 model

The recommended model is `llama3.2:3b`. On memory-constrained machines, `llama3.2:1b` can be used for comparison.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Sochjvmbcht/ai-assisted-debugging-evaluation-2.git
cd ai-assisted-debugging-evaluation-2
```

### 2. Set up the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install and start Ollama

Download the recommended model:

```bash
ollama pull llama3.2:3b
```

Ollama normally runs in the background. If it is not already running, start it in a separate terminal:

```bash
ollama serve
```

### 4. Run the unit tests

```bash
python -m unittest discover -s tests -v
```

### 5. Run the complete evaluation

```bash
python -m debugging_eval --strategy all --model llama3.2:3b --timeout 60
```

## Running Individual Strategies

Run only the structured-context strategy:

```bash
python -m debugging_eval --strategy structured
```

Run only the tool-assisted strategy:

```bash
python -m debugging_eval --strategy tool_assisted
```

Run the rule-based baseline without Ollama:

```bash
python -m debugging_eval --strategy rule_based
```

Use the smaller model:

```bash
python -m debugging_eval --strategy all --model llama3.2:1b --timeout 60
```

Repeat each strategy twice per case:

```bash
python -m debugging_eval --strategy all --model llama3.2:3b --repeats 2
```

### Tool-call configuration

The tool-assisted strategy allows one tool call by default.

You can configure the maximum number of tool calls:

```bash
python -m debugging_eval --strategy tool_assisted --max-tool-calls 0
```

```bash
python -m debugging_eval --strategy tool_assisted --max-tool-calls 2
```

The final tool-assisted interaction disables further tool calls so the model must return a diagnosis rather than continue investigating indefinitely.

## Evaluation Metrics

The framework reports the following measurements:

| Metric | Definition |
|---|---|
| Accuracy | Exact match between the normalized predicted and expected root-cause labels |
| Completeness | A non-UNKNOWN root cause, a non-empty explanation, and at least one recommended action |
| Mean latency | Average execution time across evaluated cases |
| Median latency | Middle observed execution time |
| P95 latency | Nearest-rank 95th percentile of observed execution times |
| Token usage | Prompt and completion token counters returned by Ollama |
| Tool calls | Number of inspection-tool calls made during diagnosis |
| Parse failures | Responses that cannot be parsed into the expected output format |
| Execution failures | Cases where strategy execution fails |

Latency includes the time spent on tool interactions.

## Generated Reports

After an evaluation, the framework generates:

```text
reports/
├── latest.json
├── latest.csv
└── summary.md
```

- **latest.json** — Per-case diagnoses and evaluation metadata.
- **latest.csv** — Structured results for further analysis.
- **summary.md** — Summary comparing the evaluated strategies.

## Project Structure

```text
ai-assisted-debugging-evaluation-2/
├── debugging_eval/   # CLI, Ollama client, prompts, strategies and evaluator
├── data/             # Synthetic diagnostic cases
├── reports/          # Generated evaluation reports
├── tests/            # Offline unit tests
├── .gitignore
├── LICENSE
└── README.md
```

## Limitations

- The dataset contains only 15 hand-authored synthetic cases.
- Synthetic application logs do not represent real production debugging data.
- Results cannot be generalized to cellular baseband firmware, device coredumps, or embedded systems.
- The keyword-based baseline is intentionally simple and is not a production diagnostic engine.
- LLM results may vary between runs and model versions.
- Performance measurements depend on the local machine, model, and runtime configuration.
- The inspection tools only examine supplied in-memory log text. They do not execute shell commands or access real devices.

This project is an educational experiment in LLM-assisted diagnostic workflows and evaluation methodology.

## Responsible Interpretation

Results should be interpreted only within the scope of this synthetic dataset. Accuracy on these cases does not establish reliability on real-world debugging tasks.

The purpose is to compare approaches, examine their trade-offs, and provide a reproducible foundation for further experimentation.

---

**Note:** This is an independent educational simulation. It is not affiliated with Apple and does not use Apple systems, cellular baseband firmware, real device coredumps, or production debugging infrastructure.
