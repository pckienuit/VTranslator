"""Gradio UI for the hybrid translation pipeline."""

from __future__ import annotations


import gradio as gr

from src.pipeline import create_pipeline_from_config, load_config

PIPELINE = None


def _initialize_pipeline() -> None:
    global PIPELINE

    print("=" * 70)
    print("KHỞI TẠO ỨNG DỤNG DỊCH THUẬT GEMMA (OLLAMA)")
    print("=" * 70)

    try:
        PIPELINE = create_pipeline_from_config()
        print("\n✅ Ứng dụng đã sẵn sàng (Gemma 3 12B)!")

    except Exception as exc:  # pragma: no cover - user runtime feedback
        print(f"\n❌ Lỗi khởi tạo:\n{exc}")
        PIPELINE = None


def translate_interface(input_text: str):
    if PIPELINE is None:
        error_msg = (
            "❌ Pipeline chưa được khởi tạo.\n\n"
            "Hãy đảm bảo Ollama đang chạy (`ollama serve`) và mô hình gemma3:12b đã được tải: \n"
            "    ollama pull gemma3:12b"
        )
        return "", "", error_msg

    if not input_text or not input_text.strip():
        return "", "", "⚠️ Vui lòng nhập văn bản tiếng Anh."

    try:
        result = PIPELINE.translate_and_refine(input_text)

        if "error" in result:
            return "", "", f"❌ Lỗi: {result['error']}"

        translation = result.get("translation", "")
        time_total = result.get("time_translation_sec", 0.0)
        time_info = (
            "⏱️ Thời gian xử lý:\n"
            f"  • Gemma 3 12B: {time_total:.3f}s\n\n"
            f"📊 Độ dài:\n"
            f"  • Input: {len(input_text)} ký tự\n"
            f"  • Output: {len(translation)} ký tự"
        )

        return translation, time_info, ""

    except Exception as exc:  # pragma: no cover - runtime safeguard
        return "", "", f"❌ Lỗi không mong đợi: {exc}"


def create_app() -> gr.Blocks:
    custom_css = """
    #translation_box {
        background-color: #f5f5ff !important;
    }
    """

    config = load_config()

    with gr.Blocks(
        title="Dịch thuật Gemma 3 12B (Ollama)",
        css=custom_css,
    ) as app:
        gr.Markdown(
            """
            # ✨ Dịch thuật Anh → Việt bằng Gemma 3 12B

            Toàn bộ pipeline giờ đây chỉ dùng **một mô hình Gemma 3 12B chạy qua Ollama**.
            Bạn chỉ cần cài Ollama, tải mô hình, rồi nhập văn bản tiếng Anh để nhận bản dịch tự nhiên bằng tiếng Việt.
            """
        )

        if PIPELINE is None:
            gr.Markdown(
                """
                ## ⚠️ Cần chuẩn bị Ollama

                1. Tải Ollama: https://ollama.ai/download
                2. Cài đặt rồi mở Terminal và chạy:
                   ```
                   ollama pull gemma3:12b
                   ollama serve
                   ```
                3. Khởi động lại ứng dụng với `python run_app.py`
                """
            )

        with gr.Row():
            with gr.Column(scale=1):
                input_box = gr.Textbox(
                    label="📝 Văn bản tiếng Anh",
                    placeholder="Nhập văn bản cần dịch...",
                    lines=10,
                    max_lines=20,
                )

                translate_btn = gr.Button(
                    "🚀 Dịch bằng Gemma 3 12B",
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
                translation_box = gr.Textbox(
                    label="✨ Bản dịch (Gemma 3 12B)",
                    lines=18,
                    max_lines=30,
                    interactive=False,
                    elem_id="translation_box",
                    show_copy_button=True,
                )

                time_info = gr.Textbox(
                    label="⏱️ Thời gian",
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
            - **Ollama Model:** {config.get('ollama_model', 'N/A')} (chỉnh trong `src/config/settings.json`)
            - **Máy chủ:** {config.get('ollama_host', 'N/A')}
            - **Temperature:** {config.get('temperature', 'N/A')}
            - **Giới hạn token:** {config.get('max_tokens', 'N/A')}

            Đổi mô hình bằng cách cập nhật `ollama_model` rồi chạy `ollama pull <model>`.
            """
        )

        translate_btn.click(
            fn=translate_interface,
            inputs=[input_box],
            outputs=[translation_box, time_info, error_box],
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
