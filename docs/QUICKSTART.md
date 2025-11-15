# 🚀 Quick Start - Bắt đầu trong 3 bước

Hướng dẫn siêu nhanh để chạy pipeline dịch thuật lai với Ollama.

---

## ⚡ Cài đặt tự động (Windows)

**Cách đơn giản nhất:**

```bash
scripts\setup_ollama.bat
```

Script này sẽ tự động:
- ✅ Kiểm tra Python
- ✅ Cài đặt thư viện
- ✅ Tải và chuyển đổi mô hình Stage 1
- ✅ Hướng dẫn cài Ollama

Sau khi chạy xong, làm theo hướng dẫn hiển thị để cài Ollama.

---

## 📋 Cài đặt thủ công

### Bước 1: Cài đặt thư viện

```bash
pip install ctranslate2 transformers sentencepiece gradio requests torch
```

### Bước 2: Thiết lập mô hình

```bash
python scripts/setup_models.py
```

### Bước 3: Cài đặt Ollama

#### Windows
1. Tải từ: https://ollama.ai/download
2. Chạy file `.exe` và cài đặt

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Bước 4: Tải mô hình LLM

```bash
ollama pull llama3.2:3b
```

---

## ▶️ Chạy ứng dụng

### 1. Khởi động Ollama (nếu chưa chạy)

```bash
ollama serve
```

**Lưu ý:** Trên Windows/macOS, Ollama thường tự động chạy nền sau khi cài đặt.

### 2. Chạy ứng dụng dịch thuật

```bash
python run_app.py
```

### 3. Mở trình duyệt

```
http://localhost:7860
```

---

## 🎉 Xong!

Giờ bạn có thể:
- ✅ Dịch văn bản tiếng Anh sang tiếng Việt
- ✅ Không giới hạn độ dài văn bản
- ✅ Xem cả bản dịch thô (Stage 1) và dịch tinh chỉnh (Stage 2)

---

## 📖 Tài liệu đầy đủ

- **docs/OLLAMA_GUIDE.md** - Hướng dẫn chi tiết về Ollama
- **README.md** - Tổng quan về dự án
- **docs/PROJECT_SUMMARY.md** - Tóm tắt kiến trúc và hiệu năng

---

## ❓ Gặp vấn đề?

### Lỗi: "Could not connect to Ollama"

```bash
ollama serve
```

### Lỗi: "Model not found"

```bash
ollama pull llama3.2:3b
```

### Lỗi khác

Xem **docs/OLLAMA_GUIDE.md** phần "Xử lý Lỗi"

---

**💡 Tip:** Để dịch văn bản dài, chỉ cần dán vào và chờ. Pipeline sẽ tự động xử lý!
