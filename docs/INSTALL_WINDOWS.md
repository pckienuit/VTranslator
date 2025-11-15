# 🪟 Hướng dẫn Cài đặt trên Windows

Hướng dẫn chi tiết từng bước để cài đặt pipeline dịch thuật lai trên Windows.

---

## ⚙️ Yêu cầu Hệ thống

- **Hệ điều hành**: Windows 10/11 (64-bit)
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
- **Ổ cứng**: ~5GB trống
- **GPU**: Không bắt buộc (nhưng tăng tốc nếu có NVIDIA GPU với CUDA)

---

## 📋 Cài đặt Thành phần

### 1. Cài đặt Python

#### Bước 1: Tải Python

Truy cập: https://www.python.org/downloads/

Tải phiên bản **Python 3.10** hoặc **3.11** (khuyến nghị)

#### Bước 2: Chạy trình cài đặt

**Quan trọng**: ✅ **Tích chọn "Add Python to PATH"**

![Python Install](https://docs.python.org/3/_images/win_installer.png)

Chọn "Install Now"

#### Bước 3: Kiểm tra cài đặt

Mở **Command Prompt** (Win + R → `cmd` → Enter)

```bash
python --version
```

Kết quả: `Python 3.10.x` hoặc `Python 3.11.x` → Thành công!

---

### 2. Cài đặt Ollama

#### Bước 1: Tải Ollama

Truy cập: https://ollama.ai/download

Chọn **Windows** → Tải file `.exe`

#### Bước 2: Chạy trình cài đặt

Double-click file `OllamaSetup.exe` và làm theo hướng dẫn.

#### Bước 3: Kiểm tra cài đặt

Mở **Command Prompt** mới:

```bash
ollama --version
```

Kết quả: `ollama version 0.x.x` → Thành công!

---

## 🚀 Thiết lập Pipeline

### Tự động (Khuyến nghị)

Double-click file `scripts\\setup_ollama.bat` hoặc chạy:

```bash
scripts\\setup_ollama.bat
```

Script sẽ tự động:
1. ✅ Kiểm tra Python
2. ✅ Cài đặt thư viện Python
3. ✅ Tải và chuyển đổi mô hình Stage 1
4. ✅ Hướng dẫn tải mô hình LLM

Làm theo hướng dẫn hiển thị sau khi script chạy xong.

---

### Thủ công (Nếu script tự động lỗi)

#### Bước 1: Clone/Download dự án

```bash
# Nếu có Git
git clone <repository-url> VTranslator
cd VTranslator

# Hoặc download ZIP và giải nén
```

#### Bước 2: Tạo môi trường ảo (Tùy chọn nhưng khuyến nghị)

```bash
python -m venv venv
venv\Scripts\activate
```

#### Bước 3: Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi kết nối, thêm `--proxy` nếu bạn đang sau proxy.

#### Bước 4: Thiết lập mô hình Stage 1

```bash
python scripts/setup_models.py
```

Quá trình này sẽ:
- Tải mô hình `Helsinki-NLP/opus-mt-en-vi` (~300MB)
- Chuyển đổi sang CTranslate2 với lượng tử hóa INT8

Thời gian: 3-5 phút (tùy tốc độ mạng)

#### Bước 5: Tải mô hình LLM cho Ollama

```bash
ollama pull llama3.2:3b
```

Mô hình sẽ được tải về (~2GB). Thời gian: 5-10 phút

---

## ▶️ Chạy Ứng dụng

### Bước 1: Khởi động Ollama Server

Ollama thường tự động chạy nền sau khi cài đặt trên Windows.

Kiểm tra bằng cách mở trình duyệt: http://localhost:11434

Nếu thấy "Ollama is running" → OK

Nếu không, chạy:

```bash
ollama serve
```

### Bước 2: Chạy ứng dụng dịch thuật

Mở **Command Prompt mới** (nếu đang dùng venv, activate nó):

```bash
python run_app.py
```

Kết quả:
```
Running on local URL:  http://127.0.0.1:7860
```

### Bước 3: Mở trình duyệt

Truy cập: http://localhost:7860

Bạn sẽ thấy giao diện Gradio với 2 ô:
- **Input**: Dán văn bản tiếng Anh
- **Outputs**: Stage 1 (dịch thô) và Stage 2 (tinh chỉnh)

---

## 🎯 Sử dụng

1. Dán văn bản tiếng Anh vào ô **Input**
2. Nhấn **Translate**
3. Đợi vài giây (tùy độ dài văn bản)
4. Xem kết quả ở 2 ô **Stage 1 Output** và **Stage 2 Output**

**Không giới hạn độ dài!** Bạn có thể dịch từ vài câu đến cả bài viết dài.

---

## 🐛 Xử lý Lỗi

### Lỗi: "python is not recognized"

**Nguyên nhân:** Python chưa được thêm vào PATH

**Giải pháp:**
1. Gỡ cài đặt Python
2. Cài lại và **nhớ tích** "Add Python to PATH"
3. Restart Command Prompt

### Lỗi: "No module named 'ctranslate2'"

**Nguyên nhân:** Chưa cài đặt thư viện

**Giải pháp:**
```bash
pip install ctranslate2 transformers sentencepiece gradio requests torch
```

### Lỗi: "Could not connect to Ollama"

**Nguyên nhân:** Ollama server chưa chạy

**Giải pháp:**
```bash
ollama serve
```

Hoặc kiểm tra System Tray (góc dưới cùng bên phải) có icon Ollama không

### Lỗi: "Model not found: llama3.2:3b"

**Nguyên nhân:** Chưa tải mô hình

**Giải pháp:**
```bash
ollama pull llama3.2:3b
```

### Lỗi: "Timeout waiting for response"

**Nguyên nhân:** Văn bản quá dài hoặc Ollama chậm

**Giải pháp:**

Chỉnh sửa `src/config/settings.json`:
```json
"timeout": 300
```

### Lỗi: "CUDA out of memory"

**Nguyên nhân:** GPU không đủ VRAM

**Giải pháp:**
- Ollama tự động fallback sang CPU (chậm hơn nhưng vẫn chạy)
- Hoặc dùng mô hình nhỏ hơn: `ollama pull llama3.2:3b`

---

## 🔧 Nâng cấp GPU (Tùy chọn)

Nếu bạn có GPU NVIDIA, cài đặt CUDA để tăng tốc:

### Bước 1: Cài đặt CUDA Toolkit

Tải từ: https://developer.nvidia.com/cuda-downloads

Chọn phiên bản phù hợp với driver GPU của bạn.

### Bước 2: Cài PyTorch với CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Thay `cu118` bằng phiên bản CUDA của bạn (VD: `cu121` cho CUDA 12.1)

### Bước 3: Restart ứng dụng

```bash
python run_app.py
```

Ollama và CTranslate2 sẽ tự động sử dụng GPU.

---

## 📊 Kiểm tra Hiệu năng

### Kiểm tra GPU đang được sử dụng

Mở **Task Manager** (Ctrl + Shift + Esc) → Tab **Performance** → Chọn GPU

Khi dịch, bạn sẽ thấy GPU Usage tăng lên → GPU đang được dùng

### Benchmark tốc độ

```python
import time
from pipeline_ollama import HybridTranslationPipeline

pipeline = HybridTranslationPipeline("config_ollama.json")

text = "Artificial intelligence is transforming how we interact with technology."

start = time.time()
stage1, stage2 = pipeline.translate(text)
end = time.time()

print(f"Time: {end - start:.2f}s")
```

---

## 🆘 Hỗ trợ Thêm

### Tài liệu

- **OLLAMA_GUIDE.md** - Hướng dẫn chi tiết Ollama
- **QUICKSTART.md** - Bắt đầu nhanh trong 3 bước
- **PROJECT_SUMMARY.md** - Tổng quan kiến trúc

### Video hướng dẫn (nếu có)

[Link to video tutorials]

### Community

- GitHub Issues: [Link]
- Discord/Telegram: [Link]

---

## ✅ Checklist Hoàn thành

Sau khi làm theo hướng dẫn, bạn nên có:

- ✅ Python 3.10+ cài đặt và trong PATH
- ✅ Ollama cài đặt và chạy
- ✅ Thư viện Python cài đặt (ctranslate2, transformers, etc.)
- ✅ Mô hình Stage 1 đã tải và chuyển đổi (trong `models/opus-mt-en-vi-ct2/`)
- ✅ Mô hình LLM đã tải (`ollama list` hiển thị `llama3.2:3b`)
- ✅ Ứng dụng chạy tại http://localhost:7860
- ✅ Có thể dịch văn bản không giới hạn độ dài

---

**🎉 Chúc mừng! Bạn đã thiết lập thành công pipeline dịch thuật trên Windows!**

**Bước tiếp theo**: Xem **OLLAMA_GUIDE.md** để tùy chỉnh và tối ưu pipeline.
