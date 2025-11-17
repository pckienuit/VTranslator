"""Gradio UI for the hybrid translation pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import gradio as gr

from src.pipeline import create_pipeline_from_config, load_config

PIPELINE = None


def _initialize_pipeline() -> None:
    global PIPELINE

    print("=" * 70)
    print("KHỞI TẠO ỨNG DỤNG DỊCH THUẬT LAI (OLLAMA)")
    print("=" * 70)

    try:
        config = load_config()
        base_dir = Path(__file__).resolve().parents[2]
        ct2_dir = base_dir / config["stage1_model_dir"]

        if not ct2_dir.exists() or not (ct2_dir / "model.bin").exists():
            print(f"❌ Mô hình Giai đoạn 1 chưa được chuẩn bị: {ct2_dir}")
            print("\n" + "=" * 70)
            print("⚠️  MÔ HÌNH GIAI ĐOẠN 1 CHƯA SẴN SÀNG")
            print("=" * 70)
            print("Hãy chạy lệnh sau để tải xuống và chuẩn bị mô hình:\n")
            print("    python scripts/setup_models.py\n")
            print("=" * 70)
            PIPELINE = None
            return

        print("\n🚀 Đang tải các mô hình...")
        PIPELINE = create_pipeline_from_config()
        print("\n✅ Ứng dụng đã sẵn sàng!")

    except Exception as exc:  # pragma: no cover - user runtime feedback
        print(f"\n❌ Lỗi khởi tạo:\n{exc}")
        PIPELINE = None


def translate_interface(input_text: str):
    if PIPELINE is None:
        error_msg = (
            "❌ Pipeline chưa được khởi tạo.\n\n"
            "Hãy:\n"
            "1. Chạy: python scripts/setup_models.py\n"
            "2. Cài đặt Ollama: https://ollama.ai/download\n"
            "3. Chạy: ollama pull llama3.2:3b\n"
            "4. Khởi động lại ứng dụng"
        )
        return "", "", "", error_msg

    if not input_text or not input_text.strip():
        return "", "", "", "⚠️ Vui lòng nhập văn bản tiếng Anh."

    try:
        result = PIPELINE.translate_and_refine(input_text)

        if "error" in result:
            return "", "", "", f"❌ Lỗi: {result['error']}"

        raw = result["raw_translation"]
        refined = result["refined_translation"]
        time_s1 = result["time_stage1_sec"]
        time_s2 = result["time_stage2_sec"]
        time_info = (
            "⏱️ Thời gian xử lý:\n"
            f"  • Giai đoạn 1 (Dịch thô): {time_s1:.3f}s\n"
            f"  • Giai đoạn 2 (Tinh chỉnh qua Ollama): {time_s2:.3f}s\n"
            f"  • Tổng cộng: {time_s1 + time_s2:.3f}s\n\n"
            f"📊 Độ dài:\n"
            f"  • Input: {len(input_text)} ký tự\n"
            f"  • Dịch thô: {len(raw)} ký tự\n"
            f"  • Tinh chỉnh: {len(refined)} ký tự"
        )

        return raw, refined, time_info, ""

    except Exception as exc:  # pragma: no cover - runtime safeguard
        return "", "", "", f"❌ Lỗi không mong đợi: {exc}"


def create_app() -> gr.Blocks:
    custom_css = """
    #output_refined {
        background-color: #e8f5e9 !important;
    }
    #output_raw {
        background-color: #fff3e0 !important;
    }
    """

    config = load_config()

    with gr.Blocks(
        title="Dịch thuật Lai Anh-Việt (Ollama)",
        css=custom_css,
    ) as app:
        gr.Markdown(
            """
            # 🔄 Công cụ Dịch thuật Lai Anh-Việt (Ollama)

            **Pipeline hai giai đoạn "Translate-and-Refine"**

            - **Giai đoạn 1:** Dịch thô tốc độ cao (Helsinki-NLP OPUS-MT)
            - **Giai đoạn 2:** Tinh chỉnh ngữ cảnh bằng Ollama LLM

            ---
            """
        )

        if PIPELINE is None:
            gr.Markdown(
                """
                ## ⚠️ CẢNH BÁO: Mô hình chưa được chuẩn bị

                Hãy làm theo các bước sau:

                1. **Chuẩn bị mô hình Stage 1:**
                   ```
                   python scripts/setup_models.py
                   ```

                2. **Cài đặt Ollama:**
                   - Tải từ: https://ollama.ai/download
                   - Cài đặt và khởi động Ollama

                3. **Tải mô hình LLM:**
                   ```
                   ollama pull llama3.2:3b
                   ```

                4. **Khởi động lại ứng dụng**
                """
            )

        with gr.Row():
            with gr.Column(scale=1):
                input_box = gr.Textbox(
                    label="📝 Văn bản tiếng Anh",
                    placeholder="Nhập văn bản tiếng Anh cần dịch...",
                    lines=10,
                    max_lines=20,
                )

                translate_btn = gr.Button(
                    "🚀 Dịch thuật",
                    variant="primary",
                    size="lg",
                )

                gr.Examples(
                    examples=[
                        "Hello world! This is a test of the translation system.",
                        "The enterprise solution must be robust and scalable.",
                        "Artificial intelligence is transforming the way we work and live.",
                        "Climate change poses significant challenges for future generations.",
                    ],
                    inputs=input_box,
                    label="📚 Ví dụ",
                )

            with gr.Column(scale=1):
                output_raw = gr.Textbox(
                    label="🔄 Bản dịch thô (Giai đoạn 1)",
                    lines=15,
                    max_lines=30,
                    interactive=False,
                    elem_id="output_raw",
                    show_copy_button=True,
                )

                output_refined = gr.Textbox(
                    label="✨ Bản dịch đã tinh chỉnh (Giai đoạn 2 - Ollama)",
                    lines=15,
                    max_lines=30,
                    interactive=False,
                    elem_id="output_refined",
                    show_copy_button=True,
                )

                time_info = gr.Textbox(
                    label="⏱️ Thông tin thời gian",
                    lines=4,
                    interactive=False,
                )

                error_box = gr.Textbox(
                    label="❌ Lỗi (nếu có)",
                    lines=2,
                    interactive=False,
                    visible=True,
                )

        gr.Markdown(
            f"""
            ---
            ### ⚙️ Cấu hình hiện tại
            - **Ollama Model:** {config.get('ollama_model', 'N/A')} (Điều chỉnh trong `src/config/settings.json`)
            - **Ollama Host:** {config.get('ollama_host', 'N/A')}
            - **Temperature:** {config.get('temperature', 'N/A')}

            ### 💡 Thay đổi mô hình Ollama

            Mở `src/config/settings.json` và sửa:
            ```json
            "ollama_model": "llama3.2:3b"
            ```

            **Các mô hình khuyến nghị:**
            - `llama3.2:3b` - Nhỏ, nhanh (~2GB)
            - `llama3:8b` - Cân bằng (~5GB)
            - `qwen2.5:7b` - Chất lượng cao (~5GB)

            Sau khi đổi, chạy: `ollama pull <tên-mô-hình>`
            """
        )

        translate_btn.click(
            fn=translate_interface,
            inputs=[input_box],
            outputs=[output_raw, output_refined, time_info, error_box],
        )

    return app


def main() -> None:
    _initialize_pipeline()

    app = create_app()

    print("\n" + "=" * 70)
    print("🌐 KHỞI ĐỘNG GIAO DIỆN WEB (OLLAMA)")
    print("=" * 70)
    print("Ứng dụng sẽ mở trong trình duyệt của bạn...")
    print("Nhấn Ctrl+C để dừng.")
    print("=" * 70 + "\n")

    app.launch(
        server_name="127.0.0.1",
        server_port=None,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
