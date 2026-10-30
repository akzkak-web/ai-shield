# AI Shield

AI Shield is a security baseline scanner for locally deployed AI inference
services. It discovers exposed model APIs and checks them for common
misconfigurations, producing machine-readable JSON and human-readable PDF
reports.

Current status: **v0.1.0-rc.1, internal candidate**. This release is intended
for local, authorized evaluation. It is not a full penetration-testing
platform and does not prove that a detected rule match is exploitable.

## What it does

- Discovers AI services on common ports, including non-standard local ports.
- Checks whether model-list endpoints are reachable without authentication.
- Checks model-list exposure and basic CORS posture.
- Checks whether the service is listening on loopback, private, or public
  addresses.
- Runs opt-in canary-based probes for system-prompt disclosure and synthetic
  data leakage.
- Matches known CVEs for services where a version can be reliably detected.
- Generates JSON and PDF reports with an explicit risk grade and coverage
  status.

## Non-goals

- It is not an exploitation framework.
- It does not attempt arbitrary file reads, prompt-injection jailbreaks, or
  other active attacks.
- It does not guarantee that a clean grade means a service is secure. A clean
  grade with partial or no coverage is explicitly not a safety proof.

## Supported services

| Service | Default port | Validation status |
|---|---|---|
| Ollama | 11434 | Verified against a real local Ollama service |
| vLLM | 8000 | Implemented; not verified with a real service |
| llama.cpp / LocalAI | 8080 | Implemented; not verified with a real service |
| LM Studio | 1234 | Implemented; not verified with a real service |
| Open WebUI | 3000 | Implemented; not verified with a real service |
| Text-Generation-WebUI | 7860 | Implemented; not verified with a real service |
| LocalAI | 5000 | Implemented; not verified with a real service |

Non-standard ports are detected by response content when possible.

## Checks

| Check | What it observes |
|---|---|
| `network_exposure` | Whether the target is loopback, private, or public |
| `auth_missing` | Whether `/api/tags` or `/v1/models` returns a usable model list without authentication |
| `model_access` | Whether an unauthenticated client can list models |
| `cors_check` | Whether CORS headers are permissive or reflect an arbitrary origin |
| `prompt_injection` | Opt-in canary probe for system-prompt disclosure |
| `data_leak` | Opt-in canary probe for synthetic sensitive data disclosure |
| `file_access` | Advisory-only placeholder; no active file-read exploitation |
| `resource_abuse` | Observes rate-limit headers and HTTP 429 responses |
| `cve_check` | Matches known advisories when service and version are reliably identified |

Result semantics:

| Status | Meaning |
|---|---|
| `pass` | The check ran and found no issue for the tested condition |
| `fail` | The check ran and found confirmed, evidence-backed risk |
| `unknown` | The check ran but the result could not be determined |
| `error` | The check could not run (timeout, network failure, invalid response) |

`unknown` and `error` are never silently converted into a clean pass.

## Requirements

- Python 3.9+
- pip
- A network path that can reach the Python package index during installation

Dependencies are declared in `requirements.txt`.

## Install from source

```bash
git clone https://github.com/akzkak-web/ai-shield.git
cd ai-shield
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

For development and tests:

```bash
python -m pip install -r requirements-dev.txt
```

An `install.sh` helper is also provided for local convenience. Review it
before piping it to a shell.

## Quick start

```bash
python ai-shield.py scan 127.0.0.1
python ai-shield.py scan 127.0.0.1 --ports 11434,8000
python ai-shield.py scan 127.0.0.1 --ports 11434 \
  --checks auth_missing,model_access,cors_check,network_exposure
```

Show available options:

```bash
python ai-shield.py --help
python ai-shield.py scan --help
python ai-shield.py --version
```

## Reports

JSON:

```bash
python ai-shield.py scan 127.0.0.1 --ports 11434 -o report.json
```

PDF:

```bash
python ai-shield.py scan 127.0.0.1 --ports 11434 -o report.pdf
```

Baseline and diff:

```bash
python ai-shield.py scan 127.0.0.1 --ports 11434 --baseline-out baseline.json
python ai-shield.py scan 127.0.0.1 --ports 11434 \
  --baseline baseline.json --diff-json diff.json
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Scan completed; no confirmed finding at or above the fail-gate threshold |
| 1 | Scan completed and a confirmed finding triggered the fail gate |
| 2 | Usage, target, or baseline error |

Use `--fail-on critical|high|medium|low` to set the absolute gate and
`--fail-on-new` for new findings relative to a baseline.

## Verification status

Current non-integration tests:

```text
162 passed, 4 deselected
```

PDF tests:

```text
7 passed
```

The four integration tests require Docker and a real `ollama/ollama` image;
they are intentionally not run in default CI and are marked as skipped when
Docker is unavailable. Ollama end-to-end scanning has been verified on a
loopback-bound local service.

See `docs/USER_GUIDE.md` for installation, usage, detection, and evidence
boundaries.

## Known limitations

- Only Ollama has been verified end-to-end with a real service.
- Prompt-injection and data-leak checks require explicit canary
  configuration and only produce confirmed findings on exact canary matches.
- Indirect prompt injection is not yet testable through the current scanner
  because no untrusted-context ingestion path exists.
- PDF rendering uses system fonts and falls back to Unicode-capable fonts at
  runtime; on minimal systems, PDF export may require an available CJK font.

## Contributing

Contributions are welcome. Keep changes small, add regression tests for
behavior changes, and avoid weakening existing assertions.

## Security reporting

If you find a security issue in AI Shield itself, report it responsibly
through the repository's private security advisory channel when available.
Do not include live secrets, production data, or unrelated target details.

## License

MIT License. See `LICENSE`.
