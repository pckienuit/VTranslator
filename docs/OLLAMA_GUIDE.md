# 🦙 Hướng dẫn Sử dụng Pipeline Dịch thuật với Ollama

## 📋 Giới thiệu

Phiên bản Ollama của pipeline dịch thuật lai sử dụng **Ollama** để quản lý mô hình LLM Stage 2, thay vì tải file GGUF thủ công. Cách này đơn giản hơn nhiều, đặc biệt trên Windows.

### Lợi ích của Ollama

- ✅ **Không cần biên dịch C++**: Không cần Visual Studio Build Tools
- ✅ **Quản lý mô hình dễ dàng**: Tải, cập nhật, xóa mô hình bằng 1 lệnh
- ✅ **API đơn giản**: Giao tiếp qua HTTP REST API
- ✅ **Tự động tối ưu**: Ollama tự động quản lý VRAM và hiệu năng
- ✅ **Đa nền tảng**: Hỗ trợ Windows, macOS, Linux

---

## 🚀 Cài đặt Nhanh

### 1. Cài đặt Ollama

#### Windows
```bash
# Tải từ trang chủ
https://ollama.ai/download

# Chạy file .exe và cài đặt
# Ollama sẽ tự động thêm vào PATH
```

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Kiểm tra cài đặt

```bash
ollama --version
```

Nếu thấy số phiên bản (VD: `0.1.23`) → Thành công!

---

## 🛠️ Thiết lập Pipeline

### 1. Cài đặt thư viện Python

```bash
pip install ctranslate2 transformers sentencepiece gradio requests torch
```

### 2. Thiết lập mô hình Stage 1 (CTranslate2)

```bash
python scripts/setup_models.py
```

Script này sẽ:
- Tải mô hình `Helsinki-NLP/opus-mt-en-vi`
- Chuyển đổi sang định dạng CTranslate2 với lượng tử hóa INT8

### 3. Tải mô hình LLM cho Ollama (Stage 2)

```bash
ollama pull llama3.2:3b
```

Mô hình sẽ được tải về (~2GB) và lưu trong cache của Ollama.

**Các mô hình khả dụng:**
- `llama3.2:3b` - Nhẹ, nhanh (khuyến nghị cho máy 8GB RAM)
- `llama3:8b` - Cân bằng, chất lượng tốt
- `gemma:7b` - Thay thế Google Gemma
- `mistral:7b` - Chất lượng cao

Xem danh sách đầy đủ: https://ollama.ai/library

---

## ▶️ Chạy Pipeline

### Bước 1: Khởi động Ollama Server

```bash
ollama serve
```

Ollama sẽ chạy ở `http://localhost:11434`

**Lưu ý:** 
- Trên Windows/macOS, Ollama thường tự động chạy nền sau khi cài đặt
- Kiểm tra bằng cách mở: http://localhost:11434 (sẽ thấy "Ollama is running")

### Bước 2: Chạy ứng dụng Gradio

Mở terminal/command prompt **mới** và chạy:

```bash
python run_app.py
```

Ứng dụng sẽ mở tại: http://localhost:7860

---

## 📝 Sử dụng Pipeline

### Giao diện Gradio

1. Mở trình duyệt: http://localhost:7860
2. Dán văn bản tiếng Anh vào ô **Input**
3. Nhấn **Translate**
4. Kết quả hiển thị ở **Stage 1 Output** (dịch thô) và **Stage 2 Output** (dịch tinh chỉnh)

### Ví dụ

**Input:**
```
Artificial intelligence is transforming how we interact with technology.
```

**Stage 1 Output (Dịch thô):**
```
Trí tuệ nhân tạo đang chuyển đổi cách chúng ta tương tác với công nghệ.
```

**Stage 2 Output (Tinh chỉnh):**
```
Trí tuệ nhân tạo đang thay đổi cách chúng ta tương tác với công nghệ.
```

### Không giới hạn độ dài

Pipeline **KHÔNG có giới hạn** về độ dài văn bản đầu vào. Bạn có thể dịch:
- Đoạn văn ngắn (vài câu)
- Bài viết dài (hàng ngàn từ)
- Tài liệu kỹ thuật
- Sách, báo cáo

**Lưu ý hiệu năng:**
- Văn bản dài hơn → Thời gian xử lý lâu hơn
- Ollama tự động điều chỉnh `num_predict` theo độ dài (512-4096 tokens)
- Timeout mặc định: 180 giây (có thể tăng trong `src/config/settings.json`)

---

## ⚙️ Cấu hình Nâng cao

### File `src/config/settings.json`

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

### Thay đổi mô hình LLM

1. Chỉnh sửa `ollama_model` trong `src/config/settings.json`:
   ```json
   "ollama_model": "llama3:8b"
   ```

2. Tải mô hình mới:
   ```bash
   ollama pull llama3:8b
   ```

3. Khởi động lại `python run_app.py`

### Điều chỉnh tham số

- **`temperature`** (0.0 - 1.0): Độ sáng tạo
  - `0.1-0.3`: Dịch nhất quán, ít biến thể (khuyến nghị)
  - `0.5-0.7`: Cân bằng
  - `0.8-1.0`: Dịch linh hoạt, nhiều biến thể

- **`timeout`** (giây): Thời gian chờ tối đa
  - Tăng lên nếu văn bản rất dài: `"timeout": 300`

---

## 🔧 Quản lý Mô hình Ollama

### Xem danh sách mô hình đã tải

```bash
ollama list
```

### Tải mô hình mới

```bash
ollama pull <model_name>
# Ví dụ:
ollama pull mistral:7b
```

### Xóa mô hình không dùng

```bash
ollama rm <model_name>
# Ví dụ:
ollama rm llama3.2:3b
```

### Cập nhật mô hình

```bash
ollama pull <model_name>
# Ollama sẽ tự động kiểm tra và tải phiên bản mới nhất
```

---

## 🐛 Xử lý Lỗi

### Lỗi: "Could not connect to Ollama"

**Nguyên nhân:** Ollama server chưa chạy

**Giải pháp:**
```bash
ollama serve
```

Hoặc kiểm tra Ollama đã chạy nền chưa:
- Windows: Kiểm tra System Tray
- macOS: Kiểm tra Menu Bar
- Linux: `ps aux | grep ollama`

### Lỗi: "Model not found"

**Nguyên nhân:** Mô hình chưa được tải

**Giải pháp:**
```bash
ollama pull llama3.2:3b
```

### Lỗi: "Timeout waiting for response"

**Nguyên nhân:** Văn bản quá dài hoặc mô hình chậm

**Giải pháp:**
1. Tăng `timeout` trong `src/config/settings.json`:
   ```json
   "timeout": 300
   ```

2. Hoặc dùng mô hình nhỏ hơn:
   ```bash
   ollama pull llama3.2:3b
   ```

### Lỗi: CTranslate2 không tìm thấy mô hình

**Nguyên nhân:** Chưa chạy `python scripts/setup_models.py`

**Giải pháp:**
```bash
python scripts/setup_models.py
```

---

## 📊 So sánh Phiên bản

| Tính năng | llama-cpp-python | Ollama |
|-----------|------------------|--------|
| Cài đặt Windows | ❌ Cần Build Tools | ✅ Chỉ cần .exe |
| Quản lý mô hình | 🔧 Thủ công (GGUF) | ✅ Tự động (CLI) |
| API | ⚙️ Python binding | ✅ HTTP REST |
| Hiệu năng | ⚡ Nhanh | ⚡ Tương đương |
| Khuyến nghị | Cho người dùng Linux/Mac có kinh nghiệm | **Cho mọi người, đặc biệt Windows** |

---

## 🎯 Tips & Tricks

### 1. Tăng tốc độ dịch

- Dùng mô hình nhỏ hơn (`llama3.2:3b` thay vì `llama3:8b`)
- Giảm `temperature` xuống `0.1-0.2`
- Đảm bảo Ollama chạy trên GPU (tự động nếu có CUDA/Metal)

### 2. Tăng chất lượng dịch

- Dùng mô hình lớn hơn (`llama3:8b`, `mistral:7b`)
- Tăng `temperature` lên `0.3-0.4`
- Chỉnh sửa prompt trong `src/pipeline/hybrid_pipeline.py` (nếu cần)

### 3. Dịch hàng loạt

Tạo script Python:

```python
from src.pipeline import HybridTranslationPipelineOllama

pipeline = HybridTranslationPipelineOllama.from_config()

texts = [
    "First text to translate.",
    "Second text to translate.",
    # ... many more
]

for i, text in enumerate(texts):
    stage1, stage2 = pipeline.translate(text)
    print(f"[{i+1}] Stage 2: {stage2}\n")
```

### 4. Chạy Ollama từ xa

Nếu Ollama chạy trên máy khác, đổi `ollama_host`:

```json
"ollama_host": "http://192.168.1.100:11434"
```

---

## 🆘 Hỗ trợ

### Tài liệu

- Ollama: https://ollama.ai/
- CTranslate2: https://github.com/OpenNMT/CTranslate2
- Gradio: https://gradio.app/

### Báo lỗi

Nếu gặp lỗi, hãy kiểm tra:
1. Ollama đã chạy chưa: `curl http://localhost:11434`
2. Mô hình đã tải chưa: `ollama list`
3. Thư viện Python: `pip list | grep ctranslate2`

---

## 🚀 Bước tiếp theo

Sau khi thiết lập thành công, bạn có thể:

1. **Tùy chỉnh giao diện**: Chỉnh sửa `src/app/web_ui.py` (Gradio)
2. **Thử mô hình khác**: `ollama pull mistral:7b`
3. **Tích hợp vào ứng dụng**: Import `HybridTranslationPipeline`
4. **Triển khai lên server**: Dùng Gradio sharing hoặc Docker

---

**🎉 Chúc bạn dịch thuật hiệu quả với Ollama!**
