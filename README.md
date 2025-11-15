# VTranslator – Hybrid English→Vietnamese Pipeline

A production-grade **Translate-and-Refine** system that marries the speed of CTranslate2 NMT with the fluency of an Ollama-hosted LLM. Everything is organized into a modern Python package layout (`src/`), with scripts, docs, and runnable entry points to keep maintenance simple.

---

## ✨ Key Features

- **Two-stage translation** – Stage 1 uses `Helsinki-NLP/opus-mt-en-vi` via CTranslate2 (INT8) for fast, accurate drafts. Stage 2 refines the result with any Ollama model (default `llama3.2:3b`).
- **Unlimited input size** – Dynamic `num_predict` (up to 16k tokens) plus a 10-minute timeout lets you translate full chapters.
- **Cross-platform setup** – Windows/macOS/Linux supported. No local GGUF juggling or CUDA builds; Ollama handles the LLM runtime.
- **Gradio web UI** – Clean interface with latency stats, plus an importable pipeline for scripting/automation.
- **Well-structured repo** – `src/` package, `scripts/` utilities, and `docs/` references keep everything tidy.

---

## 🧱 Repository Structure

```
VTranslator/
├── docs/                         # Guides, quick starts, install notes, project summary
├── models/                       # Generated Stage 1 models (created by setup script)
├── scripts/
│   ├── setup_models.py           # Downloads & converts Stage 1 model
│   └── setup_ollama.bat          # Windows one-click installer
├── src/
│   ├── app/
│   │   └── web_ui.py             # Gradio Blocks UI
│   ├── config/
│   │   └── settings.json         # Central configuration
│   └── pipeline/
│       ├── __init__.py
│       └── hybrid_pipeline.py    # Translate-and-refine implementation
├── requirements.txt              # Python dependencies
├── run_app.py                    # Entry point to launch the UI
└── README.md
```

---

## 🛠️ Prerequisites

| Component   | Requirement                                                     |
|-------------|-----------------------------------------------------------------|
| Python      | 3.10+ (recommend 3.11)                                          |
| Pip/Virtualenv | Latest pip, optional `python -m venv venv`                   |
| Stage 1 deps | `pip install -r requirements.txt`                              |
| Stage 2 deps | Ollama (https://ollama.ai/download)                            |
| Hardware    | CPU-only works; GPU (CUDA/Metal) improves latency automatically |

> **Note:** You no longer need Visual Studio Build Tools or `llama-cpp-python`. Ollama provides the LLM runtime via HTTP.

---

## 🚀 Quick Start

### 1. Clone & (optionally) create a virtual env

```bash
git clone <repo-url>
cd VTranslator
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Stage 1 model (CTranslate2)

```bash
python scripts/setup_models.py
```

This downloads `Helsinki-NLP/opus-mt-en-vi` and converts it to INT8 CTranslate2 weights under `models/opus-mt-en-vi-ct2`.

### 4. Setup Stage 2 (Ollama)

```bash
ollama pull llama3.2:3b
ollama serve  # usually auto-starts on Windows/macOS
```

> Prefer automation? Run `scripts/setup_ollama.bat` on Windows to handle steps 2–4 with prompts.

### 5. Launch the UI

```bash
python run_app.py
```

Open http://localhost:7860 and drop in English source text. Stage 1 and Stage 2 outputs plus timings are shown side-by-side.

---

## ⚙️ Configuration (`src/config/settings.json`)

```json
{
  "stage1_model_dir": "models/opus-mt-en-vi-ct2",
  "stage1_hf_name": "Helsinki-NLP/opus-mt-en-vi",
  "ollama_model": "llama3.2:3b",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.2,
  "beam_size": 2,
  "timeout": 600
}
```

- `ollama_model`: switch to `llama3:8b`, `mistral:7b`, `qwen2.5:7b`, etc., then run `ollama pull <name>`.
- `timeout`: bump to 900+ seconds for extremely long documents.
- `stage1_model_dir`: where converted CTranslate2 weights are stored (relative to repo root).

---

## 📦 Using the Pipeline Programmatically

```python
from src.pipeline import create_pipeline_from_config

pipeline = create_pipeline_from_config()
result = pipeline.translate_and_refine("Artificial intelligence is reshaping marketing.")

print("Stage 1:", result["raw_translation"])
print("Stage 2:", result["refined_translation"])
print("Latency:", result["time_stage1_sec"] + result["time_stage2_sec"], "s")
```

---

## 📚 Documentation

All reference materials live in `docs/`:

- `docs/QUICKSTART.md` – three-step starter guide
- `docs/INSTALL_WINDOWS.md` – Windows-specific walkthrough
- `docs/OLLAMA_GUIDE.md` – everything about Ollama usage & troubleshooting
- `docs/PROJECT_SUMMARY.md` – architecture & performance recap

---

## 🧪 Verification

After every change, run a quick smoke test:

```bash
python scripts/setup_models.py  # ensures Stage 1 assets exist
ollama serve                    # ensure Ollama is running
python run_app.py               # launch UI
```

The UI banner will confirm model readiness; try one of the sample prompts to verify both stages respond.

---

## 🤝 Contributing

1. Fork & branch (`git checkout -b feature/idea`)
2. Keep code under `src/` and add docs/tests as needed
3. Run the smoke test above
4. Submit a PR with a summary + screenshots (if UI changes)

---

## 📄 License

Code is released under the MIT License (see `LICENSE`). Upstream model licenses apply individually (Helsinki-NLP OPUS-MT, Meta Llama 3, etc.).

---

Happy translating! 💫
