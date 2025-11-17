"""Gemma-only translation pipeline powered by Ollama."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "src" / "config"


class GemmaTranslationPipeline:
    """Single-stage translation pipeline that talks to Ollama."""

    def __init__(
        self,
        ollama_model: str = "gemma3:12b",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        max_chunk_chars: int = 1200,
        timeout: int = 600,
    ) -> None:
        self.ollama_model = ollama_model
        self.ollama_host = ollama_host.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_chunk_chars = max(200, max_chunk_chars)
        self.timeout = timeout

        print("🚀 Khởi tạo GemmaTranslationPipeline (Ollama-only)")
        self._check_ollama()
        print("✅ Pipeline đã sẵn sàng!")

    # ------------------------------------------------------------------
    # Ollama helpers
    # ------------------------------------------------------------------
    def _check_ollama(self) -> None:
        print("\n📦 Kiểm tra Ollama server")
        print(f"   Host: {self.ollama_host}")
        print(f"   Model: {self.ollama_model}")

        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise ConnectionError(
                "❌ Không thể kết nối tới Ollama. Hãy đảm bảo dịch vụ đang chạy bằng `ollama serve`."
            ) from exc

        models = response.json().get("models", [])
        available = {model.get("name") for model in models}
        if self.ollama_model not in available:
            print(f"   ⚠️ Mô hình '{self.ollama_model}' chưa có sẵn. Đang tải...")
            self._pull_model(self.ollama_model)
        else:
            print("   ✅ Mô hình đã được tải")

    def _pull_model(self, model_name: str) -> None:
        try:
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=max(self.timeout, 600),
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue
                status = json.loads(line).get("status", "")
                if status:
                    print(f"   📥 {status}")

            print(f"   ✅ Đã tải mô hình '{model_name}'")
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Không thể tải mô hình '{model_name}'. Hãy chạy thủ công: ollama pull {model_name}"
            ) from exc

    # ------------------------------------------------------------------
    # Translation helpers
    # ------------------------------------------------------------------
    def _chunk_text(self, text: str) -> List[str]:
        text = text.strip()
        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks: List[str] = []
        current = []
        current_len = 0

        sentences = [s.strip() for s in text.replace("\r", "").split("\n") if s.strip()]
        for sentence in sentences:
            if current_len + len(sentence) + 1 > self.max_chunk_chars and current:
                chunks.append(" ".join(current).strip())
                current = []
                current_len = 0

            current.append(sentence)
            current_len += len(sentence) + 1

        if current:
            chunks.append(" ".join(current).strip())

        return chunks or [text]

    def _build_prompt(self, chunk: str, index: int, total: int) -> str:
        header = f"Đoạn {index}/{total}." if total > 1 else "Văn bản cần dịch."
        return (
            f"{header}\n\n"
            "Hãy dịch đoạn tiếng Anh sau sang tiếng Việt tự nhiên, giữ nguyên các tên riêng/thuật ngữ tiếng Anh "
            "và có thể thêm ghi chú ngắn trong ngoặc. Không giải thích, chỉ trả về bản dịch.\n\n"
            f"Đoạn tiếng Anh:\n{chunk}\n\nBản dịch tiếng Việt:"
        )

    def _call_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "system": (
                        "Bạn là dịch giả tiếng Anh sang tiếng Việt. Dịch mượt, chính xác, giữ nguyên tên riêng và "
                        "thêm chú thích ngắn trong ngoặc nếu cần. Chỉ trả về bản dịch."
                    ),
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                        "repeat_penalty": 1.1,
                    },
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Lỗi khi gọi Ollama: {exc}") from exc

        result = response.json().get("response", "").strip()
        for prefix in ("Bản dịch:", "Bản dịch tiếng Việt:", "Vietnamese:", "Translation:"):
            if result.startswith(prefix):
                result = result[len(prefix):].strip()
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def translate_and_refine(self, text_to_translate: str) -> Dict[str, object]:
        if not text_to_translate or not text_to_translate.strip():
            return {
                "source": "",
                "translation": "",
                "time_translation_sec": 0.0,
                "error": "Văn bản đầu vào trống",
            }

        start = time.time()
        chunks = self._chunk_text(text_to_translate)
        translations: List[str] = []

        for idx, chunk in enumerate(chunks, 1):
            prompt = self._build_prompt(chunk, idx, len(chunks))
            translations.append(self._call_ollama(prompt))

        translation = "\n\n".join(t for t in translations if t)
        duration = time.time() - start

        return {
            "source": text_to_translate,
            "translation": translation.strip(),
            "time_translation_sec": duration,
        }


def load_config(config_path: Optional[str] = None) -> Dict[str, object]:
    path = Path(config_path) if config_path else CONFIG_DIR / "settings.json"
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình: {path}")

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def create_pipeline_from_config(config_path: Optional[str] = None) -> GemmaTranslationPipeline:
    config = load_config(config_path)
    return GemmaTranslationPipeline(
        ollama_model=config.get("ollama_model", "gemma3:12b"),
        ollama_host=config.get("ollama_host", "http://localhost:11434"),
        temperature=config.get("temperature", 0.2),
        max_tokens=config.get("max_tokens", 2048),
        max_chunk_chars=config.get("max_chunk_chars", 1200),
        timeout=config.get("timeout", 600),
    )