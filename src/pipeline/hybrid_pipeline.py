"""Hybrid translation pipeline powered by CTranslate2 and Ollama."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import ctranslate2
import requests
import transformers

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "src" / "config"


class HybridTranslationPipelineOllama:
    """Translate-and-refine pipeline that uses Ollama for refinement."""

    def __init__(
        self,
        ct2_model_dir: str,
        hf_model_name: str,
        ollama_model: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.2,
        beam_size: int = 2,
    ) -> None:
        print("🚀 Đang khởi tạo Pipeline Dịch thuật Lai (Ollama)...")

        self.ollama_model = ollama_model
        self.ollama_host = ollama_host
        self.temperature = temperature
        self.beam_size = beam_size
        self.translator: Optional[ctranslate2.Translator] = None
        self.tokenizer: Optional[transformers.PreTrainedTokenizer] = None

        self._init_stage1(ct2_model_dir, hf_model_name)
        self._check_ollama()

        print("✅ Pipeline đã sẵn sàng!")

    def _init_stage1(self, ct2_model_dir: str, hf_model_name: str) -> None:
        print("\n📦 Giai đoạn 1: Tải mô hình CTranslate2")
        print(f"   Đường dẫn: {ct2_model_dir}")

        if not os.path.exists(ct2_model_dir):
            raise FileNotFoundError(
                f"❌ Thư mục mô hình CTranslate2 '{ct2_model_dir}' không tìm thấy.\n"
                "   Hãy chạy: python scripts/setup_models.py"
            )

        try:
            self.translator = ctranslate2.Translator(ct2_model_dir, device="cuda")
            print("   ✅ Đã tải trên CUDA (GPU)")
        except Exception as exc:  # pragma: no cover - hardware dependent
            print(f"   ⚠️  Không thể tải trên CUDA: {exc}")
            print("   🔄 Đang chuyển sang CPU...")
            self.translator = ctranslate2.Translator(ct2_model_dir, device="cpu")
            print("   ✅ Đã tải trên CPU")

        print(f"   Đang tải tokenizer: {hf_model_name}")
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(hf_model_name)
        print("   ✅ Tokenizer đã sẵn sàng")

    def _check_ollama(self) -> None:
        print("\n📦 Giai đoạn 2: Kiểm tra Ollama")
        print(f"   Host: {self.ollama_host}")
        print(f"   Model: {self.ollama_model}")

        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError("Ollama server không phản hồi")

            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]

            if self.ollama_model not in model_names:
                print(f"   ⚠️  Mô hình '{self.ollama_model}' chưa được tải")
                print("   📥 Đang tải mô hình... (có thể mất vài phút)")
                self._pull_ollama_model()
            else:
                print("   ✅ Mô hình đã sẵn sàng")

        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(
                f"❌ Không thể kết nối đến Ollama tại {self.ollama_host}\n\n"
                "Hãy đảm bảo Ollama đang chạy:\n"
                "1. Tải Ollama: https://ollama.ai/download\n"
                "2. Cài đặt và khởi động Ollama\n"
                f"3. Chạy: ollama pull {self.ollama_model}\n"
                "4. Chạy lại ứng dụng"
            ) from exc

    def _pull_ollama_model(self) -> None:
        try:
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": self.ollama_model},
                stream=True,
                timeout=600,
            )

            for line in response.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                status = data.get("status", "")
                if "pulling" in status.lower():
                    print(f"   📥 {status}")

            print("   ✅ Mô hình đã được tải")

        except Exception as exc:
            raise RuntimeError(
                f"❌ Lỗi khi tải mô hình Ollama:\n{exc}\n\n"
                f"Hãy tải thủ công: ollama pull {self.ollama_model}"
            ) from exc

    def _translate_stage1(self, source_text: str) -> str:
        assert self.tokenizer is not None
        assert self.translator is not None

        source_text_with_token = f">>vie<< {source_text}"
        source_tokens = self.tokenizer.convert_ids_to_tokens(
            self.tokenizer.encode(source_text_with_token)
        )

        results = self.translator.translate_batch(
            [source_tokens],
            beam_size=self.beam_size,
        )

        target_tokens = results[0].hypotheses[0]
        target_text = self.tokenizer.decode(
            self.tokenizer.convert_tokens_to_ids(target_tokens),
            skip_special_tokens=True,
        )

        return target_text

    def _refine_stage2(self, source_text: str, raw_translation: str) -> str:
        prompt = f"""Improve this Vietnamese translation to make it natural and fluent:

English: {source_text}

Current Vietnamese: {raw_translation}

Improved Vietnamese:"""

        estimated_tokens = len(raw_translation) // 3 + 200
        max_tokens = min(max(estimated_tokens, 1024), 16384)

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "system": (
                        "You are a Vietnamese translation editor. Your only job is to "
                        "improve Vietnamese translations. Output ONLY the improved "
                        "Vietnamese text, with no explanations or comments."
                    ),
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": max_tokens,
                        "stop": ["English:", "Original:", "Source:", "Note:"],
                    },
                },
                timeout=600,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama API lỗi: {response.status_code}")

            result = response.json()
            refined_text = result.get("response", "").strip()

            prefixes_to_remove = [
                "Improved Vietnamese:",
                "Improved:",
                "Translation:",
                "Vietnamese:",
            ]
            for prefix in prefixes_to_remove:
                if refined_text.startswith(prefix):
                    refined_text = refined_text[len(prefix):].strip()

            return refined_text if refined_text else raw_translation

        except requests.exceptions.Timeout as exc:
            raise TimeoutError("Ollama API timeout. Thử lại hoặc tăng timeout.") from exc
        except Exception as exc:
            raise RuntimeError(f"Lỗi khi gọi Ollama: {exc}") from exc

    def translate_and_refine(self, text_to_translate: str) -> Dict:
        if not text_to_translate or not text_to_translate.strip():
            return {
                "source": "",
                "raw_translation": "",
                "refined_translation": "",
                "time_stage1_sec": 0.0,
                "time_stage2_sec": 0.0,
                "error": "Văn bản đầu vào trống",
            }

        start_s1 = time.time()
        try:
            raw_translation = self._translate_stage1(text_to_translate)
        except Exception as exc:
            return {
                "source": text_to_translate,
                "raw_translation": "",
                "refined_translation": "",
                "time_stage1_sec": 0.0,
                "time_stage2_sec": 0.0,
                "error": f"Lỗi Giai đoạn 1: {exc}",
            }
        end_s1 = time.time()

        start_s2 = time.time()
        try:
            refined_translation = self._refine_stage2(text_to_translate, raw_translation)
        except Exception as exc:
            return {
                "source": text_to_translate,
                "raw_translation": raw_translation,
                "refined_translation": "",
                "time_stage1_sec": end_s1 - start_s1,
                "time_stage2_sec": 0.0,
                "error": f"Lỗi Giai đoạn 2: {exc}",
            }
        end_s2 = time.time()

        return {
            "source": text_to_translate,
            "raw_translation": raw_translation,
            "refined_translation": refined_translation,
            "time_stage1_sec": end_s1 - start_s1,
            "time_stage2_sec": end_s2 - start_s2,
        }


def load_config(config_path: Optional[str] = None) -> Dict:
    if config_path is None:
        config_path = CONFIG_DIR / "settings.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Không tìm thấy config tại: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_pipeline_from_config(config_path: Optional[str] = None) -> HybridTranslationPipelineOllama:
    config = load_config(config_path)

    repo_root = Path(__file__).resolve().parents[2]
    ct2_dir = repo_root / config["stage1_model_dir"]

    return HybridTranslationPipelineOllama(
        ct2_model_dir=str(ct2_dir),
        hf_model_name=config["stage1_hf_name"],
        ollama_model=config.get("ollama_model", "llama3:8b"),
        ollama_host=config.get("ollama_host", "http://localhost:11434"),
        temperature=config.get("temperature", 0.2),
        beam_size=config.get("beam_size", 2),
    )


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO: PIPELINE DỊCH THUẬT LAI (OLLAMA)")
    print("=" * 70)

    try:
        pipeline = create_pipeline_from_config()
    except Exception as exc:  # pragma: no cover - manual demo
        print(f"\n❌ Lỗi khởi tạo pipeline:\n{exc}")
        print("\n💡 Hãy chạy: python scripts/setup_models.py")
        print("💡 Và đảm bảo Ollama đang chạy")
        sys.exit(1)

    test_texts = [
        "Hello world! This is a test of the translation system.",
        "The enterprise solution must be robust and scalable.",
        "Artificial intelligence is transforming the way we work.",
    ]

    for idx, text in enumerate(test_texts, 1):
        print(f"\n{'=' * 70}")
        print(f"VĂN BẢN THỬ NGHIỆM #{idx}")
        print(f"{'=' * 70}")

        result = pipeline.translate_and_refine(text)

        if "error" in result:
            print(f"❌ LỖI: {result['error']}")
            continue

        print("\n📝 Nguồn:")
        print(f"   {result['source']}")
        print(f"\n🔄 Thô (Giai đoạn 1 - {result['time_stage1_sec']:.3f}s):")
        print(f"   {result['raw_translation']}")
        print(f"\n✨ Tinh chỉnh (Giai đoạn 2 - {result['time_stage2_sec']:.3f}s):")
        print(f"   {result['refined_translation']}")
        print(
            f"\n⏱️  Tổng thời gian: {result['time_stage1_sec'] + result['time_stage2_sec']:.3f}s"
        )

    print(f"\n{'=' * 70}")
    print("✅ DEMO HOÀN TẤT")
    print("=" * 70)
