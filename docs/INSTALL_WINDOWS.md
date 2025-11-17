# 🪟 Hướng dẫn cài đặt VTranslator trên Windows (Gemma-only)

Pipeline hiện chỉ cần Ollama + Gemma 3 12B, vì vậy việc cài đặt nhẹ hơn rất nhiều so với phiên bản lai trước đây.

---

## 1. Chuẩn bị Python

1. Tải Python 3.10 hoặc 3.11 từ https://www.python.org/downloads/
2. Khi cài đặt, nhớ tick **"Add Python to PATH"**.
3. Mở Command Prompt và kiểm tra:
   ```cmd
   python --version
   ```

(Tùy chọn) Tạo môi trường ảo:
```cmd
python -m venv venv
venv\Scripts\activate
```

---

## 2. Cài đặt thư viện Python

Trong thư mục dự án:
```cmd
pip install -r requirements.txt
```

Chỉ còn `gradio` và `requests`, nên bước này rất nhanh.

---

## 3. Cài đặt Ollama và tải Gemma

1. Tải Ollama cho Windows: https://ollama.ai/download
2. Chạy file cài đặt `OllamaSetup.exe`
3. Mở Command Prompt mới và chạy:
   ```cmd
   ollama pull gemma3:12b
   ollama serve
   ```
   Lần kéo đầu tiên mất ~2–3GB dung lượng.

---

## 4. Chạy ứng dụng

```cmd
python run_app.py
```

Mặc định Gradio mở tại http://127.0.0.1:7860. Nhập văn bản tiếng Anh và nhấn **“Dịch bằng Gemma 3 12B”**.

---

## 5. Kiểm tra nhanh

- `ollama serve` đang chạy và hiển thị trong system tray.
- `ollama list` có `gemma3:12b`.
- UI trả về bản dịch duy nhất cùng thời gian xử lý.

---

## 6. Xử lý lỗi phổ biến

| Lỗi | Cách khắc phục |
| --- | --- |
| `python is not recognized` | Cài lại Python và tick “Add Python to PATH” |
| `Could not connect to Ollama` | Chạy `ollama serve` hoặc mở lại ứng dụng Ollama |
| `Model not found: gemma3:12b` | Chạy `ollama pull gemma3:12b` |
| Proxy/vpn chặn Ollama | Dùng VPN khác hoặc mạng không proxy |

---

## 7. Checklist cuối

- ✅ Python 3.10+ trong PATH
- ✅ Đã cài `pip install -r requirements.txt`
- ✅ Ollama đang chạy (`ollama serve`)
- ✅ `ollama list` hiển thị `gemma3:12b`
- ✅ `python run_app.py` mở giao diện thành công

Chúc bạn dịch thuật vui vẻ! ✨
