# Mô hình đang dùng

Pipeline hiện chạy **một giai đoạn duy nhất** với `gemma3:12b` thông qua Ollama. Việc loại bỏ các model CTranslate2 giúp cấu hình gọn nhẹ và nhất quán trên mọi máy.

## Vì sao chọn Gemma 3 12B
- Chất lượng dịch tự nhiên, giữ nguyên thuật ngữ và nội dung trong ngoặc
- Ít lặp từ, hạn chế biến mất nội dung quan trọng ở văn bản dài
- Hoạt động tốt với prompt hướng dẫn dịch ngữ cảnh mà pipeline đang dùng

## Yêu cầu tài nguyên
| Thành phần | Tối thiểu | Khuyến nghị |
|------------|-----------|-------------|
| RAM        | 8GB       | 16GB        |
| CPU        | 4 cores   | 8 cores     |
| GPU        | Không bắt buộc | 12GB VRAM nếu dùng GPU backend |
| Disk       | ~15GB (model + cache) | 20GB |

## Thông số Ollama
`src/config/settings.json` lưu cấu hình chính:
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
Điều chỉnh nhiệt độ hoặc số token tối đa tùy nhu cầu. Nếu chạy Ollama trên máy khác, cập nhật `ollama_host` cho đúng địa chỉ.

## Có thể đổi model khác không?
Bạn vẫn có thể thử các model khác của Ollama (ví dụ `gemma2:9b`, `llama3.1:8b`) bằng cách sửa `ollama_model`. Toàn bộ prompt và UI hiện được tinh chỉnh cho `gemma3:12b`, nên chất lượng cao nhất vẫn đạt với cấu hình mặc định.

## Kiểm tra nhanh
```cmd
ollama pull gemma3:12b
ollama run gemma3:12b "Dịch câu này sang tiếng Việt"
```
Nếu lệnh thử nghiệm phản hồi bình thường, bạn có thể chạy `python run_app.py` để mở giao diện web.
