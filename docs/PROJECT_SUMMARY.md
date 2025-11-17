# 📊 PROJECT SUMMARY - Tóm tắt Dự án

## 🎯 Mục tiêu

Triển khai pipeline dịch thuật lai **Translate-and-Refine** hai giai đoạn:
1. **Stage 1**: Dịch thô nhanh bằng mô hình NMT nhẹ
2. **Stage 2**: Tinh chỉnh bằng mô hình ngôn ngữ lớn (LLM)

Mục tiêu: Kết hợp **tốc độ** (Stage 1) và **chất lượng** (Stage 2).

---

## 🏗️ Kiến trúc

### Stage 1: Neural Machine Translation (NMT)

- **Mô hình**: `Helsinki-NLP/opus-mt-en-vi`
- **Framework**: CTranslate2 (optimized inference engine)
- **Lượng tử hóa**: INT8 (giảm VRAM, tăng tốc độ)
- **VRAM**: ~813MB
- **Tốc độ**: ~9x nhanh hơn PyTorch baseline
- **Vai trò**: Dịch thô nhanh từ English → Vietnamese

### Stage 2: Large Language Model (LLM)

#### Phiên bản Ollama (Khuyến nghị)

- **Mô hình**: `llama3.2:3b` (hoặc `llama3:8b`, `mistral:7b`)
- **Framework**: Ollama API (HTTP REST)
- **Quản lý**: Ollama tự động xử lý VRAM và model loading
- **Prompt**: English, system message, stop tokens
- **Timeout**: 180s (có thể điều chỉnh)
- **Vai trò**: Tinh chỉnh dịch thô, cải thiện fluency và naturalness

#### Phiên bản llama-cpp-python (Không dùng)

- **Lý do bỏ**: Requires Visual Studio Build Tools trên Windows
- **Thay thế bằng**: Ollama

---

## 📁 Cấu trúc Dự án

### Files chính (Phiên bản Ollama)

```
VTranslator/
│
├── app_ollama.py              # Gradio UI cho Ollama
├── pipeline_ollama.py         # Core pipeline với Ollama
├── config_ollama.json         # Cấu hình Ollama
├── setup_models.py            # Script thiết lập mô hình Stage 1
├── setup_ollama.bat           # Auto-install cho Windows
│
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
│
├── OLLAMA_GUIDE.md           # Hướng dẫn chi tiết Ollama
├── QUICKSTART.md             # Bắt đầu nhanh trong 3 bước
├── README.md                 # Tổng quan dự án
├── PROJECT_SUMMARY.md        # File này
├── LICENSE                   # MIT License
│
└── models/                   # Thư mục lưu mô hình (tự tạo)
    └── opus-mt-en-vi-ct2/    # CTranslate2 model (sau khi chạy setup)
```

### Files legacy (Không dùng)

```
├── app.py                    # Gradio UI cho llama-cpp-python
├── pipeline.py               # Core pipeline với llama-cpp-python
├── config.json               # Cấu hình cho llama-cpp-python
```

---

## 🔧 Cấu hình

### `config_ollama.json`

```json
{
  "stage1_hf_name": "Helsinki-NLP/opus-mt-en-vi",
  "stage1_model_dir": "models/opus-mt-en-vi-ct2",
  "ollama_model": "llama3.2:3b",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.2,
  "timeout": 180
}
```

**Tham số quan trọng:**
- `ollama_model`: Tên mô hình LLM (xem `ollama list`)
# 📊 PROJECT SUMMARY

## 🎯 Mục tiêu
Cung cấp trình dịch Anh → Việt chất lượng cao dựa trên **một giai đoạn duy nhất** của mô hình `gemma3:12b` chạy qua Ollama. Pipeline tập trung vào sự đơn giản: chỉ cần cài Ollama, kéo model, cấu hình thông số, rồi chạy UI Gradio.

---

## 🏗️ Kiến trúc hiện tại
```
Văn bản nguồn + bối cảnh
        ↓
[GemmaTranslationPipeline]
        ↓
Kết quả dịch đã tinh chỉnh
```
- Không còn Stage 1 NMT; Gemma đảm nhiệm cả dịch thô lẫn tinh chỉnh.
- Pipeline chia văn bản thành từng chunk, thêm prompt hướng dẫn giữ nguyên thuật ngữ, rồi ghép kết quả cuối.
- UI (`src/app/web_ui.py`) giao tiếp với pipeline thông qua API cục bộ.

---

## 📁 Cấu trúc chính
```
VTranslator/
├── run_app.py                    # Entry point Gradio
├── src/
│   ├── app/web_ui.py            # Giao diện web
│   ├── pipeline/gemma_pipeline.py
│   ├── pipeline/hybrid_pipeline.py (shim tương thích)
│   └── config/settings.json     # Tham số Ollama + chunk
├── scripts/
│   ├── setup_models.py          # Kiểm tra phụ thuộc, hướng dẫn kéo model
│   └── setup_ollama.bat         # Quy trình cài đặt trên Windows
├── docs/                        # README, QUICKSTART, INSTALL_WINDOWS, OLLAMA_GUIDE, ...
├── requirements.txt             # Chỉ cần gradio + requests
└── README.md                    # Tổng quan dự án
```

---

## ⚙️ Cấu hình
`src/config/settings.json` điều khiển toàn bộ hành vi:
```json
{
  "ollama_model": "gemma3:12b",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.15,
  "max_tokens": 2048,
  "max_chunk_chars": 2100,
  "timeout": 120.0
}
```
- `max_chunk_chars`: giới hạn số ký tự một đoạn gửi lên Ollama; tự động ghép lại.
- `max_tokens`: số token trả về tối đa mỗi lần gọi.
- `timeout`: thời gian chờ API.

---

## 🧠 Prompt Engineering
System prompt nhắc Gemma đóng vai dịch giả kỹ thuật, giữ định dạng, không bỏ nội dung. User prompt bao gồm:
1. Ngữ cảnh/bối cảnh dịch
2. Văn bản gốc tiếng Anh
3. Hướng dẫn yêu cầu đầu ra tiếng Việt rõ ràng

Pipeline tự động loại bỏ nhãn “Vietnamese Translation:” nếu model trả về.

---

## 🚀 Quy trình sử dụng
1. Cài Ollama (xem `docs/INSTALL_WINDOWS.md` hoặc `docs/OLLAMA_GUIDE.md`).
2. Chạy `ollama pull gemma3:12b`.
3. Tạo môi trường Python và `pip install -r requirements.txt`.
4. Chạy `python run_app.py`.
5. Mở URL Gradio, nhập văn bản + bối cảnh, nhấn "Translate".

---

## 📈 Hiệu năng & Giới hạn
- Chất lượng dịch phụ thuộc vào Gemma; tốc độ ~5-10s cho đoạn 400 từ (tùy phần cứng).
- Không giới hạn độ dài văn bản; pipeline sẽ tự chia nhỏ.
- Cần RAM tối thiểu 8GB và khoảng 15GB đĩa trống cho model.

---

## 🔧 Tùy chỉnh
- Muốn dùng model khác: sửa `ollama_model` và kéo model tương ứng.
- Muốn thay prompt: chỉnh `GemmaTranslationPipeline._build_prompt`.
- Muốn đổi UI: cập nhật `src/app/web_ui.py` (Gradio components).

---

## 📚 Tài liệu liên quan
- `README.md` – Tổng quan và hướng dẫn chung
- `docs/QUICKSTART.md` – 3 bước chạy nhanh
- `docs/INSTALL_WINDOWS.md` – Hướng dẫn đầy đủ cho Windows
- `docs/OLLAMA_GUIDE.md` – Chi tiết thiết lập Ollama
- `docs/MODELS.md` – Thông tin model Gemma đang dùng

---

## ✅ Kết luận
Phiên bản hiện tại nhấn mạnh sự đơn giản: một mô hình duy nhất, cấu hình nhẹ, dễ vận hành. Chỉ cần Ollama + Gemma 3 12B là có thể dịch chất lượng cao mà không phải quản lý nhiều pipeline phức tạp.
Chỉnh sửa `pipeline_ollama.py`:
