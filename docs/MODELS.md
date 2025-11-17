# So sánh các mô hình dịch Anh-Việt

## Tổng quan

Pipeline hỗ trợ nhiều mô hình Stage 1 khác nhau. Dưới đây là so sánh chi tiết:

---

## 1. OPUS-MT (Helsinki-NLP) - MẶC ĐỊNH

**Model:** `Helsinki-NLP/opus-mt-en-vi`

### Ưu điểm:
- ✅ Nhẹ (~300MB)
- ✅ Rất nhanh
- ✅ Dễ cài đặt
- ✅ Hỗ trợ sẵn trong pipeline

### Nhược điểm:
- ❌ Chất lượng trung bình
- ❌ Hay bị lặp từ với văn bản dài
- ❌ Dịch máy móc, ít tự nhiên

### Khi nào dùng:
- Cần tốc độ cao
- Văn bản ngắn (<200 từ)
- Dịch nhanh để tham khảo

### Cài đặt:
```bash
python scripts/setup_models.py
```

---

## 2. M2M100 (Facebook/Meta) - ĐỀ XUẤT

**Model:** `facebook/m2m100_418M` hoặc `facebook/m2m100_1.2B`

### Ưu điểm:
- ✅ Chất lượng tốt hơn OPUS-MT rõ rệt
- ✅ Ít lặp từ hơn
- ✅ Hỗ trợ 100 ngôn ngữ
- ✅ Dịch tự nhiên hơn

### Nhược điểm:
- ❌ Lớn hơn (418MB - 1.2GB)
- ❌ Chậm hơn OPUS-MT ~20-30%
- ❌ Cần cấu hình thêm

### Khi nào dùng:
- Cần chất lượng cao
- Văn bản dài (>200 từ)
- Sẵn sàng đánh đổi tốc độ

### Cài đặt:

#### Bước 1: Tải và convert model
```bash
# Cài thêm package
pip install sentencepiece

# Chạy script setup
python scripts/setup_m2m100.py
```

Chọn kích thước:
- `1` = 418M (nhanh, đủ tốt)
- `2` = 1.2B (chậm hơn, chất lượng cao nhất)

#### Bước 2: Cập nhật config
Sửa `src/config/settings.json`:
```json
{
  "stage1_model_dir": "models/m2m100-418m-ct2",
  "stage1_hf_name": "facebook/m2m100_418M",
  "use_ollama_only": false,
  ...
}
```

---

## 3. NLLB (Facebook/Meta)

**Model:** `facebook/nllb-200-distilled-600M`

### Ưu điểm:
- ✅ Chất lượng rất tốt
- ✅ Hỗ trợ 200 ngôn ngữ
- ✅ Đa dạng phong cách dịch

### Nhược điểm:
- ❌ Rất lớn (600MB - 3.3GB)
- ❌ Chậm nhất
- ❌ Cần RAM nhiều

### Khi nào dùng:
- Cần chất lượng cao nhất
- Máy cấu hình mạnh
- Không quan tâm tốc độ

### Cài đặt:
```bash
# Tự động tải và convert (chưa có script)
# Sẽ được thêm trong tương lai
```

---

## 4. Ollama Only - CHẤT LƯỢNG CAO NHẤT

**Model:** Sử dụng LLM (Gemma, Llama, v.v.) trực tiếp

### Ưu điểm:
- ✅ Chất lượng xuất sắc
- ✅ Không bị lặp từ
- ✅ Dịch tự nhiên như người
- ✅ Giữ nguyên thuật ngữ + dịch trong ngoặc

### Nhược điểm:
- ❌ RẤT chậm (5-10x chậm hơn)
- ❌ Cần model LLM lớn (>3B params)
- ❌ Tốn tài nguyên

### Khi nào dùng:
- Văn bản quan trọng
- Cần chất lượng tối đa
- Sẵn sàng đợi lâu

### Cài đặt:
Sửa `src/config/settings.json`:
```json
{
  "use_ollama_only": true,
  "ollama_model": "gemma3:12b",
  ...
}
```

---

## So sánh hiệu năng

| Model | Tốc độ | Chất lượng | Kích thước | Lặp từ | RAM |
|-------|--------|------------|------------|--------|-----|
| **OPUS-MT** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 300MB | ❌ Nhiều | 2GB |
| **M2M100-418M** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 418MB | ✅ Ít | 3GB |
| **M2M100-1.2B** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1.2GB | ✅ Rất ít | 4GB |
| **NLLB-600M** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 600MB | ✅ Rất ít | 4GB |
| **Ollama Only** | ⭐ | ⭐⭐⭐⭐⭐ | Depends | ✅ Không | 8GB+ |

---

## Khuyến nghị

### Cho máy yếu (RAM <4GB):
- Dùng **OPUS-MT** + repetition_penalty
- Hoặc M2M100-418M nếu chịu chậm hơn

### Cho máy trung bình (RAM 4-8GB):
- Dùng **M2M100-418M** (đề xuất)
- Hoặc M2M100-1.2B cho chất lượng cao

### Cho máy mạnh (RAM >8GB, GPU):
- Dùng **M2M100-1.2B**
- Hoặc **Ollama Only** với model lớn

### Cho production:
- Dùng **M2M100-418M** + Ollama Stage 2
- Balance tốt giữa tốc độ và chất lượng

---

## Gỡ lỗi

### Lỗi lặp từ:
1. Thử tăng `repetition_penalty` trong code
2. Giảm `beam_size` xuống 1
3. Chuyển sang M2M100 hoặc Ollama Only

### Lỗi OOM (out of memory):
1. Giảm `max_decoding_length`
2. Chia văn bản thành chunks nhỏ hơn
3. Chuyển sang model nhỏ hơn

### Dịch quá chậm:
1. Dùng OPUS-MT thay vì M2M100
2. Giảm `beam_size` xuống 1
3. Tắt `use_ollama_only`
