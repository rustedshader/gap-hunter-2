# Gap Hunter Studio

Gap Hunter Studio is a policy gap analysis engine that aligns internal policies to the CIS MS-ISAC NIST CSF Policy Template Guide (2024) and produces revised policies in the NIST template format. This repo now ships with a production-grade Electron desktop app plus the Python backend.

## What you get

- Electron desktop app with live logs, status telemetry, progress stages, artifacts, and summaries.
- Ollama URL support (recommended) or local GGUF model support.
- Fully packaged backend binary via PyInstaller and Electron Builder.

## Local development

### Backend (Python)

Install Python dependencies with `uv`:

```bash
uv sync
```

Run the CLI directly:

```bash
python src/main.py <policy.pdf> --ollama-url http://localhost:11434 --model gemma4:e2b
```

### Electron app (UI)

Install frontend dependencies:

```bash
cd app
npm install
```

Run the app in dev mode (Electron + Vite):

```bash
npm run dev
```

The dev app uses the repo's `.venv` automatically. Make sure `uv sync` has been
run so dependencies like `langchain_community` are available. If you need a
custom interpreter, set `GAP_HUNTER_PYTHON`.

To open Electron devtools during development, set `ELECTRON_DEVTOOLS=1`.

If your Python executable is not on PATH, set `GAP_HUNTER_PYTHON` before running:

```bash
export GAP_HUNTER_PYTHON=/path/to/python
```

## Packaging (fully bundled binaries)

1. Build the backend binary (PyInstaller):

```bash
uv run python packaging/build_backend.py
```

The backend binary is staged into the Electron resources folder. See [packaging/build_backend.py](packaging/build_backend.py).

2. Package the Electron app:

```bash
cd app
npm run build
```

This builds the renderer, bundles the backend, and produces platform installers via Electron Builder.

### Cross-platform builds

Electron Builder produces OS-specific artifacts. Build each target on its native OS (macOS, Windows, Linux), or use CI runners for each platform.

## LLM configuration

You can switch providers in the UI or pass flags to the CLI.

### Ollama (recommended)

- Start Ollama locally or point to a remote server.
- Provide the base URL (for example `http://localhost:11434`).
- Set a model name (for example `gemma4:e2b`).

CLI example:

```bash
python src/main.py <policy.pdf> --ollama-url http://localhost:11434 --model gemma4:e2b
```

### Local GGUF (llama.cpp)

If you want to run locally without Ollama, set a GGUF model path:

```bash
python src/main.py <policy.pdf> --llm-provider llamacpp --gguf-model-path /path/to/model.gguf
```

## Key files

- App entry: [app/electron/main.js](app/electron/main.js)
- UI source: [app/src/renderer/App.tsx](app/src/renderer/App.tsx)
- Backend CLI: [src/main.py](src/main.py)
- LLM provider factory: [src/llm.py](src/llm.py)
- PyInstaller spec: [packaging/backend.spec](packaging/backend.spec)

## Testing

Gap-Hunter-2 includes a comprehensive research-based testing framework with 4 test phases:

- **Unit Tests**: Fast deterministic tests (<5s) for core logic validation
- **Integration Tests**: Multi-agent architecture tests with mocked LLMs (<30s)
- **E2E Tests**: Golden dataset tests with real LLM calls and LLM-as-a-judge evaluation
- **Adversarial Tests**: Robustness tests against corrupted/malicious inputs

### Running Tests

```bash
# Run fast tests (unit + integration)
PYTHONPATH=. uv run pytest -m "unit or integration" tests/

# Run all tests
PYTHONPATH=. uv run pytest tests/

# Run with coverage
PYTHONPATH=. uv run pytest tests/ --cov=src --cov-report=html:tests/reports/coverage/full
```

### CI/CD Pipelines

- **Fast CI**: Runs on every push/PR (unit + integration tests, <2 min)
- **Nightly E2E**: Scheduled at 2 AM UTC (golden dataset + adversarial tests, 30-60 min)
- **Full Test Suite**: Manual trigger (all test phases, 45-75 min)

### Test Reports

After running tests, view the dashboard:

```bash
open tests/reports/index.html
```

For detailed testing documentation, see [tests/README.md](tests/README.md).

## Notes

- Output reports are written under the default reports folder unless overridden.
- The app surfaces all output files inside the run directory.
- Ollama models are not bundled; the app connects to your Ollama server at runtime.
