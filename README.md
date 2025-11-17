# VTranslator – Gemma 3 12B English→Vietnamese Pipeline

VTranslator is now a **single-stage** translator powered entirely by the `gemma3:12b` model running inside Ollama. The legacy CTranslate2 “Stage 1” draft has been removed, which keeps the repo lighter, easier to maintain, and focused on one high-quality model.

---

## ✨ Highlights

- **Gemma-only pipeline** – just pull `gemma3:12b` in Ollama and start translating.
- **Lean dependencies** – no CTranslate2, no Hugging Face converters, only `requests` + `gradio`.
- **Chunk-aware prompting** – long passages are automatically split/stitched for stable performance.
- **Refreshed Gradio UI** – single polished output with timing stats.
- **Importable module** – use the same pipeline object in scripts or automations.

---

## 🧱 Repository Structure

```
VTranslator/
├── docs/                         # Guides, quick starts, project summary
├── scripts/
│   ├── setup_models.py           # Verifies deps, reminds you to pull Gemma
│   └── setup_ollama.bat          # Windows helper for the same
├── src/
│   ├── app/
│   │   └── web_ui.py             # Gradio Blocks UI
│   ├── config/
│   │   └── settings.json         # Central configuration
│   └── pipeline/
│       ├── __init__.py
│       └── gemma_pipeline.py     # Gemma 3 12B implementation
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
| Dependencies | `pip install -r requirements.txt`                              |
| Ollama      | Install from https://ollama.ai/download and run `ollama serve`  |
| Hardware    | CPU-only works; GPU (CUDA/Metal) improves latency automatically |

> **Note:** You no longer need Visual Studio Build Tools or `llama-cpp-python`. Ollama provides the LLM runtime via HTTP.

---

## 🚀 Quick Start

1. **Clone & (optionally) create a virtual env**
  ```bash
  git clone <repo-url>
  cd VTranslator
  python -m venv venv
  venv\Scripts\activate  # or source venv/bin/activate
  ```

2. **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

3. **Install & prepare Ollama**
  ```bash
  # after installing Ollama from https://ollama.ai
  ollama pull gemma3:12b
  ollama serve
  ```

4. **(Optional) Run the helper script** – it simply checks Python deps and prints the Ollama commands again.
  ```bash
  python scripts/setup_models.py
  ```

5. **Launch the UI**
  ```bash
  python run_app.py
  ```
  Open the Gradio link (default http://127.0.0.1:7860) and paste any English passage.

---

## ⚙️ Configuration (`src/config/settings.json`)

```json
{
  "ollama_model": "gemma3:12b",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.2,
  "max_tokens": 2048,
  "max_chunk_chars": 1200,
  "timeout": 600
}
```

- `ollama_model`: change to any other Ollama model (remember `ollama pull <model>`).
- `max_chunk_chars`: adjust if you prefer larger/smaller chunks per request.
- `max_tokens`/`temperature`: forwarded directly to the Ollama `/api/generate` call.

---

## 📦 Using the Pipeline Programmatically

```python
from src.pipeline import create_pipeline_from_config

pipeline = create_pipeline_from_config()
result = pipeline.translate_and_refine("Artificial intelligence is reshaping marketing.")

print("Translation:\n", result["translation"])
print("Latency:", result["time_translation_sec"], "s")
```

---

## 📚 Documentation

All reference materials live in `docs/`:

- `docs/QUICKSTART.md` – Gemma-only quick start
- `docs/INSTALL_WINDOWS.md` – Windows-specific walkthrough
- `docs/OLLAMA_GUIDE.md` – Ollama usage & troubleshooting
- `docs/MODELS.md` – recommended Ollama models
- `docs/PROJECT_SUMMARY.md` – updated architecture recap

---

## 🧪 Verification

After every change, run a quick smoke test:

```bash
pip install -r requirements.txt
ollama pull gemma3:12b
ollama serve                    # ensure Ollama is running
python run_app.py               # launch UI
```

Use one of the built-in examples to confirm the single-stage output looks good.

---

## 🤝 Contributing

1. Fork & branch (`git checkout -b feature/idea`)
2. Keep code under `src/` and add docs/tests as needed
3. Run the smoke test above
4. Submit a PR with a summary + screenshots (if UI changes)

---

## 📄 License

Code is released under the MIT License (see `LICENSE`). Upstream model licenses (Gemma 3, other Ollama models) apply individually.

---

Happy translating! 💫
