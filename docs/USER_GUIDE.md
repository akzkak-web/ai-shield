# AI Shield User Guide

This guide describes the current `v0.1.0-rc.1` behavior and evidence
boundaries for internal evaluation.

## 1. Installation and environment

AI Shield is a Python application. The supported quick start is a local
virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

The runtime requirements are:

- Python 3.9+
- `fastapi`
- `uvicorn`
- `httpx`
- `pydantic`
- `fpdf2`

Development tests additionally use `pytest`.

The `install.sh` helper installs into `~/.ai-shield` and creates a launcher.
It is provided for convenience and should be reviewed before use.

## 2. CLI usage

```bash
python ai-shield.py --help
python ai-shield.py scan --help
python ai-shield.py --version
```

Common commands:

```bash
python ai-shield.py scan 127.0.0.1
python ai-shield.py scan 127.0.0.1 --ports 11434,8000
python ai-shield.py scan 127.0.0.1 --ports 11434 -o report.json
python ai-shield.py scan 127.0.0.1 --ports 11434 -o report.pdf
```

Available scan options:

- `--ports`
- `--checks`
- `--allow-private`
- `--fail-on`
- `--baseline`
- `--baseline-out`
- `--diff-json`
- `--fail-on-new`
- `-o, --output`

Global option:

- `--version`

## 3. Output format

JSON reports contain:

- `id`, `target`, `start_time`, `end_time`, `duration`
- `grade`, `risk_score`, `grade_reasons`
- `coverage`, `coverage_status`
- `notes`
- `port_data`
- `findings`
- `check_results`
- `summary`

PDF reports render the same findings with a risk grade and per-finding
evidence. PDF text uses system font discovery with CJK fallback where
available.

## 4. Detections and finding semantics

Every check returns one of:

- `pass`
- `fail`
- `unknown`
- `error`

Only `fail` creates a finding. `unknown` and `error` reduce coverage instead
of becoming findings.

Confirmed findings are driven by deterministic evidence, such as:

- an unauthenticated non-empty model list;
- an exact configured canary in the user-visible model response.

The letter grade is based on the worst confirmed finding. Coverage status is
independent and describes how much of the scan was actually verified.

## 5. Testing and reproducible evidence

Fast unit and mock tests:

```bash
python -m pytest -q -m "not integration"
```

PDF-focused tests:

```bash
python -m pytest -q tests/test_report.py
```

Compile check:

```bash
python -m compileall -q ai-shield.py core checks services web tests
```

Real-service integration tests are under `tests/integration/` and require
Docker plus a local `ollama/ollama` image. They are not part of the fast CI
suite.

## 6. Known limitations and support matrix

- Ollama is the only service validated end-to-end with a real local service.
- vLLM, LocalAI, LM Studio, Open WebUI, and Text-Generation-WebUI have code
  paths but have not been verified against real instances.
- Prompt-injection and data-leak checks require explicit canary environment
  variables and exact matches.
- Indirect prompt injection is not testable with the current scanner.

## 7. Internal trial checklist

1. Install into an isolated virtual environment.
2. Run `python ai-shield.py --help` and `scan --help`.
3. Run a loopback-only minimal scan.
4. Generate JSON and PDF reports and inspect both.
5. Review `unknown` and `error` coverage separately from findings.
6. Do not treat a grade of A with partial coverage as a security guarantee.
