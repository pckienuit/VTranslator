"""Minimal setup helper for the Gemma-only pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "src" / "config" / "settings.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
        return json.load(stream)


def verify_requirements() -> None:
    print("\n=" * 30)
    print("KIỂM TRA THƯ VIỆN PYTHON")
    print("=" * 60)

    required = ["requests", "gradio"]
    missing = []
    for module in required:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - chưa cài")
            missing.append(module)

    if missing:
        print("\n⚠️ Hãy cài đặt các thư viện còn thiếu:")
        print("   pip install -r requirements.txt")
        sys.exit(1)


def print_ollama_instructions(config: dict) -> None:
    model = config.get("ollama_model", "gemma3:12b")
    print("\n" + "=" * 60)
    print("OLLAMA / GEMMA 3 12B")
    print("=" * 60)
    print("1. Cài đặt Ollama: https://ollama.ai/download")
    print("2. Mở terminal và chạy:")
    print(f"   ollama pull {model}")
    print("   ollama serve")
    print("3. Khởi động ứng dụng: python run_app.py")


def main() -> None:
    print("=" * 60)
    print("THIẾT LẬP GEMMA TRANSLATOR")
    print("=" * 60)

    verify_requirements()
    config = load_config()
    print("\n✅ Đã đọc cấu hình Gemma")
    print_ollama_instructions(config)


if __name__ == "__main__":
    main()
