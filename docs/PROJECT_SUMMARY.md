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
- `temperature`: Độ sáng tạo (0.1-0.3 cho dịch thuật)
- `timeout`: Thời gian chờ tối đa (giây)

---

## ⚙️ Quy trình Dịch thuật

### Pipeline Workflow

```
English Input
     ↓
[Tokenization] (sentencepiece)
     ↓
[Stage 1: CTranslate2 NMT]
     ↓
Vietnamese Draft (thô)
     ↓
[Stage 2: Ollama LLM]
     ↓
Vietnamese Refined (tinh chỉnh)
```

### Stage 2 Prompt Engineering

**System Message:**
```
You are a translation refinement assistant. Your task is to improve Vietnamese translations.
```

**User Prompt:**
```
Improve this Vietnamese translation:
{translation}

Output only the improved Vietnamese text, nothing else.
```

**Stop Tokens:** `["\n\n", "English:", "Current", "Improved"]`

---

## 📊 Hiệu năng

### Tốc độ (Stage 1 - CTranslate2)

| Metric | Giá trị |
|--------|---------|
| Inference Speed | ~9x faster than PyTorch |
| VRAM Usage | ~813MB (INT8 quantization) |
| Model Size | ~300MB (on disk) |

### Chất lượng (Stage 2 - Ollama)

| Metric | Mô tả |
|--------|-------|
| Fluency | Cải thiện tính tự nhiên của câu |
| Consistency | Giữ nguyên ý nghĩa gốc |
| Naturalness | Tiếng Việt tự nhiên hơn, ít máy móc |

---

## 🚀 Cài đặt & Sử dụng

### Quick Start

```bash
# 1. Tự động (Windows)
setup_ollama.bat

# 2. Thủ công
pip install ctranslate2 transformers sentencepiece gradio requests torch
python setup_models.py
ollama pull llama3.2:3b

# 3. Chạy
ollama serve
python app_ollama.py
```

Xem **QUICKSTART.md** để biết chi tiết.

---

## 🎛️ Tùy chỉnh

### Thay đổi mô hình LLM

1. Chỉnh sửa `config_ollama.json`:
   ```json
   "ollama_model": "llama3:8b"
   ```

2. Tải mô hình:
   ```bash
   ollama pull llama3:8b
   ```

3. Restart `app_ollama.py`

### Điều chỉnh prompt

Chỉnh sửa `pipeline_ollama.py`:

```python
def _refine_stage2(self, translation: str) -> str:
    system = "Your custom system message"
    user = f"Your custom user prompt with {translation}"
    # ...
```

### Không giới hạn độ dài

Pipeline **KHÔNG có giới hạn** về độ dài văn bản:
- ✅ `app_ollama.py`: Không có check độ dài
- ✅ `pipeline_ollama.py`: `num_predict` tự động từ 512-4096 tokens
- ✅ `timeout`: 180s (có thể tăng lên)

---

## 🆚 So sánh Phiên bản

| Feature | llama-cpp-python | Ollama |
|---------|------------------|--------|
| **Windows Install** | ❌ Cần Build Tools | ✅ Chỉ cần .exe |
| **Model Management** | 🔧 Thủ công (GGUF) | ✅ CLI (pull/rm) |
| **API** | ⚙️ Python binding | ✅ HTTP REST |
| **Performance** | ⚡ Fast | ⚡ Equivalent |
| **Ease of Use** | 🔴 Advanced users | 🟢 Beginner friendly |
| **Recommendation** | Linux/Mac experts | **Everyone** |

---

## 🐛 Troubleshooting

### Lỗi: "Could not connect to Ollama"

```bash
ollama serve
```

### Lỗi: "Model not found"

```bash
ollama list
ollama pull llama3.2:3b
```

### Lỗi: "Timeout"

Tăng `timeout` trong `config_ollama.json`:
```json
"timeout": 300
```

Xem **OLLAMA_GUIDE.md** để biết thêm.

---

## 📚 Dependencies

### Python Packages

```
ctranslate2>=3.24.0
transformers>=4.36.0
sentencepiece>=0.1.99
torch>=2.1.0
gradio>=4.0.0
requests>=2.31.0
```

### External Tools

- **Ollama**: https://ollama.ai/download
- **Python**: 3.8+ (khuyến nghị 3.10+)

---

## 📖 Tài liệu

- **QUICKSTART.md** - Bắt đầu nhanh trong 3 bước
- **OLLAMA_GUIDE.md** - Hướng dẫn chi tiết về Ollama
- **README.md** - Tổng quan và giới thiệu
- **LICENSE** - MIT License

---

## 🎯 Kết luận

Dự án VTranslator cung cấp:
- ✅ **Pipeline dịch thuật lai** hiệu quả (Translate-and-Refine)
- ✅ **Không giới hạn độ dài** văn bản đầu vào
- ✅ **Dễ cài đặt** trên Windows với Ollama
- ✅ **Linh hoạt** trong việc chọn mô hình LLM
- ✅ **Hiệu năng cao** với CTranslate2 và Ollama

**Phiên bản Ollama** là lựa chọn khuyến nghị cho mọi người dùng, đặc biệt trên Windows.

---

**🚀 Bắt đầu ngay: `setup_ollama.bat`**
