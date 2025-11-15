"""Download and convert Stage 1 models for the hybrid pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "src" / "config" / "settings.json"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"❌ Lỗi: Không tìm thấy file cấu hình tại {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def setup_stage1_model(config):
    print("\n" + "=" * 60)
    print("GIAI ĐOẠN 1: Thiết lập Mô hình Dịch thuật (CTranslate2)")
    print("=" * 60)

    model_dir = config["stage1_model_dir"]
    hf_name = config["stage1_hf_name"]

    models_dir = REPO_ROOT / "models"
    models_dir.mkdir(exist_ok=True)

    output_dir = REPO_ROOT / model_dir

    if output_dir.exists() and (output_dir / "model.bin").exists():
        print(f"✅ Mô hình CTranslate2 đã tồn tại tại: {output_dir}")
        print("   Bỏ qua bước chuyển đổi.")
        return True

    print(f"📥 Đang tải và chuyển đổi mô hình: {hf_name}")
    print(f"   Đích: {output_dir}")
    print("   Cấu hình: Lượng tử hóa INT8 (tối ưu cho VRAM)")
    print("\n⏳ Quá trình này có thể mất vài phút...")

    cmd = [
        "ct2-transformers-converter",
        "--model",
        hf_name,
        "--output_dir",
        str(output_dir),
        "--quantization",
        "int8",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\n✅ Chuyển đổi thành công!")
        print(f"   Mô hình đã được lưu tại: {output_dir}")
        return True

    except subprocess.CalledProcessError as exc:
        print("\n❌ Lỗi khi chuyển đổi mô hình:")
        print(f"   {exc.stderr}")
        return False
    except FileNotFoundError:
        print("\n❌ Lỗi: Không tìm thấy lệnh 'ct2-transformers-converter'")
        print("   Hãy đảm bảo bạn đã cài đặt ctranslate2:")
        print("   pip install ctranslate2")
        return False


def setup_stage2_model(config):
    print("\n" + "=" * 60)
    print("GIAI ĐOẠN 2: Thiết lập Mô hình Tinh chỉnh (Ollama)")
    print("=" * 60)

    ollama_model = config.get("ollama_model", "llama3.2:3b")

    print(f"📋 Phiên bản Ollama sử dụng mô hình: {ollama_model}")
    print()
    print("✅ Mô hình LLM sẽ được quản lý bởi Ollama.")
    print("   Không cần tải GGUF thủ công!")
    print()
    print("📝 Hướng dẫn:")
    print("   1. Cài đặt Ollama: https://ollama.ai/download")
    print(f"   2. Tải mô hình: ollama pull {ollama_model}")
    print("   3. Khởi động Ollama: ollama serve")
    print()
    print("💡 Để đổi mô hình, chỉnh sửa 'ollama_model' trong src/config/settings.json")
    print("   Sau đó chạy: ollama pull <tên-mô-hình-mới>")

    return True


def verify_installation():
    print("\n" + "=" * 60)
    print("KIỂM TRA THÀNH PHẦN")
    print("=" * 60)

    required_packages = {
        "ctranslate2": "ctranslate2",
        "transformers": "transformers",
        "sentencepiece": "sentencepiece",
        "gradio": "gradio",
        "requests": "requests",
    }

    all_installed = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - CHƯA CÀI ĐẶT")
            all_installed = False

    if not all_installed:
        print("\n⚠️  Một số thư viện chưa được cài đặt.")
        print(
            "   Chạy: pip install ctranslate2 transformers sentencepiece gradio requests torch"
        )
        return False

    return True


def main():
    print("=" * 60)
    print("THIẾT LẬP PIPELINE DỊCH THUẬT LAI (OLLAMA)")
    print("=" * 60)
    print("Script này sẽ tải xuống và chuẩn bị mô hình Stage 1.")
    print("Mô hình LLM Stage 2 sẽ được quản lý bởi Ollama.")
    print()

    if not verify_installation():
        sys.exit(1)

    config = load_config()
    print("\n✅ Đã đọc cấu hình từ src/config/settings.json")

    if not setup_stage1_model(config):
        print("\n❌ Thiết lập Giai đoạn 1 thất bại.")
        sys.exit(1)

    setup_stage2_model(config)

    print("\n" + "=" * 60)
    print("✅ HOÀN TẤT THIẾT LẬP STAGE 1")
    print("=" * 60)
    print("Mô hình dịch thô đã sẵn sàng!")
    print("\nBước tiếp theo:")
    print("1. Cài đặt Ollama từ: https://ollama.ai/download")
    print(f"2. Tải mô hình LLM: ollama pull {config.get('ollama_model', 'llama3.2:3b')}")
    print("3. Chạy ứng dụng: python run_app.py")
    print("\n💡 Hoặc chạy script tự động: scripts/setup_ollama.bat")


if __name__ == "__main__":
    main()
