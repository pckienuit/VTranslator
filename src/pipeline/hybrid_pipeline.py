"""Hybrid translation pipeline powered by CTranslate2 and Ollama."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import ctranslate2
import requests
import transformers

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "src" / "config"


class HybridTranslationPipelineOllama:
    """Translate-and-refine pipeline that uses Ollama for refinement."""

    def __init__(
        self,
        ct2_model_dir: str,
        hf_model_name: str,
        ollama_model: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.2,
        beam_size: int = 2,
        use_ollama_only: bool = False,  # Chỉ dùng Ollama, bỏ qua Stage 1
    ) -> None:
        print("🚀 Đang khởi tạo Pipeline Dịch thuật Lai (Ollama)...")

        self.ollama_model = ollama_model
        self.ollama_host = ollama_host
        self.temperature = temperature
        self.beam_size = beam_size
        self.use_ollama_only = use_ollama_only
        self.translator: Optional[ctranslate2.Translator] = None
        self.tokenizer: Optional[transformers.PreTrainedTokenizer] = None

        if not use_ollama_only:
            self._init_stage1(ct2_model_dir, hf_model_name)
        else:
            print("\n⚡ Chế độ: Chỉ dùng Ollama (bỏ qua CTranslate2)")
            
        self._check_ollama()

        print("✅ Pipeline đã sẵn sàng!")

    def _get_lang_token(self, lang_code: str) -> Optional[str]:
        """Return tokenizer token string for a given language code."""
        tokenizer = getattr(self, "tokenizer", None)
        if tokenizer is None:
            return None

        if getattr(self, "model_type", None) == "m2m100":
            # Try lang_code_to_token first
            token = getattr(tokenizer, "lang_code_to_token", {}).get(lang_code)
            if token:
                return token
            if hasattr(tokenizer, "get_lang_id"):
                try:
                    token_id = tokenizer.get_lang_id(lang_code)
                    return tokenizer.convert_ids_to_tokens([token_id])[0]
                except Exception:
                    return None

        return None

    def _build_source_tokens(self, text: str) -> list[str]:
        """Convert raw text into token list compatible with translator."""
        assert self.tokenizer is not None

        if getattr(self, "model_type", None) == "m2m100":
            self.tokenizer.src_lang = "en"
            encoded_ids = self.tokenizer.encode(text, add_special_tokens=True)
            return self.tokenizer.convert_ids_to_tokens(encoded_ids)

        encoded_ids = self.tokenizer.encode(f">>vie<< {text}")
        return self.tokenizer.convert_ids_to_tokens(encoded_ids)

    def _init_stage1(self, ct2_model_dir: str, hf_model_name: str) -> None:
        print("\n📦 Giai đoạn 1: Tải mô hình CTranslate2")
        print(f"   Đường dẫn: {ct2_model_dir}")

        if not os.path.exists(ct2_model_dir):
            raise FileNotFoundError(
                f"❌ Thư mục mô hình CTranslate2 '{ct2_model_dir}' không tìm thấy.\n"
                "   Hãy chạy: python scripts/setup_models.py"
            )

        try:
            self.translator = ctranslate2.Translator(ct2_model_dir, device="cuda")
            print("   ✅ Đã tải trên CUDA (GPU)")
        except Exception as exc:  # pragma: no cover - hardware dependent
            print(f"   ⚠️  Không thể tải trên CUDA: {exc}")
            print("   🔄 Đang chuyển sang CPU...")
            self.translator = ctranslate2.Translator(ct2_model_dir, device="cpu")
            print("   ✅ Đã tải trên CPU")

        print(f"   Đang tải tokenizer: {hf_model_name}")
        
        # Kiểm tra loại model để load đúng tokenizer
        if "m2m100" in hf_model_name.lower():
            self.tokenizer = transformers.M2M100Tokenizer.from_pretrained(hf_model_name)
            self.model_type = "m2m100"
            self.tokenizer.src_lang = "en"
            self.tokenizer.tgt_lang = "vi"
            print("   📝 Loại: M2M100 (Facebook)")
        else:
            self.tokenizer = transformers.AutoTokenizer.from_pretrained(hf_model_name)
            self.model_type = "opus"
            print("   📝 Loại: OPUS-MT (Helsinki)")
            
            # Kiểm tra và thiết lập target language cho OPUS-MT
            if hasattr(self.tokenizer, 'tgt_lang'):
                self.tokenizer.tgt_lang = 'vi'
                print("   🎯 Target language: vi (Vietnamese)")
            if hasattr(self.tokenizer, 'src_lang'):
                self.tokenizer.src_lang = 'en'
                print("   🎯 Source language: en (English)")
            print("   📝 Loại: OPUS-MT (Helsinki)")
            
        print("   ✅ Tokenizer đã sẵn sàng")

    def _check_ollama(self) -> None:
        print("\n📦 Giai đoạn 2: Kiểm tra Ollama")
        print(f"   Host: {self.ollama_host}")
        print(f"   Model: {self.ollama_model}")

        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError("Ollama server không phản hồi")

            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]

            if self.ollama_model not in model_names:
                print(f"   ⚠️  Mô hình '{self.ollama_model}' chưa được tải")
                print("   📥 Đang tải mô hình... (có thể mất vài phút)")
                self._pull_ollama_model()
            else:
                print("   ✅ Mô hình đã sẵn sàng")

        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(
                f"❌ Không thể kết nối đến Ollama tại {self.ollama_host}\n\n"
                "Hãy đảm bảo Ollama đang chạy:\n"
                "1. Tải Ollama: https://ollama.ai/download\n"
                "2. Cài đặt và khởi động Ollama\n"
                f"3. Chạy: ollama pull {self.ollama_model}\n"
                "4. Chạy lại ứng dụng"
            ) from exc

    def _pull_ollama_model(self) -> None:
        try:
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": self.ollama_model},
                stream=True,
                timeout=600,
            )

            for line in response.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                status = data.get("status", "")
                if "pulling" in status.lower():
                    print(f"   📥 {status}")

            print("   ✅ Mô hình đã được tải")

        except Exception as exc:
            raise RuntimeError(
                f"❌ Lỗi khi tải mô hình Ollama:\n{exc}\n\n"
                f"Hãy tải thủ công: ollama pull {self.ollama_model}"
            ) from exc

    def _split_text(self, text: str, max_tokens: int = 400) -> list[str]:
        """Chia văn bản thành các đoạn nhỏ hơn max_tokens."""
        assert self.tokenizer is not None
        
        print(f"\n   🔍 DEBUG: Đang chia văn bản ({len(text)} ký tự)...")
        
        # Chia theo câu - regex phức tạp hơn để xử lý footnote, số, v.v.
        import re
        # Tìm dấu kết thúc câu: . ! ? theo sau bởi space và chữ hoa HOẶC cuối văn bản
        # Nhưng không phải số thập phân (1.5) hoặc viết tắt phổ biến
        sentence_ends = re.finditer(r'([.!?]+)\s+(?=[A-Z])|([.!?]+)$', text)
        
        positions = [0]
        for match in sentence_ends:
            end_pos = match.end()
            if end_pos < len(text):
                positions.append(end_pos)
        positions.append(len(text))
        
        # Tạo list các câu
        sentences = []
        for i in range(len(positions) - 1):
            sentence = text[positions[i]:positions[i+1]].strip()
            if sentence:
                sentences.append(sentence)
        
        print(f"   📝 Chia được {len(sentences)} câu từ regex")
        
        # Nếu không chia được câu, chia theo đoạn văn
        if len(sentences) <= 1:
            paragraphs = text.split('\n')
            sentences = [p.strip() for p in paragraphs if p.strip()]
            print(f"   📝 Fallback: Chia theo đoạn văn → {len(sentences)} đoạn")
        
        # Ghép câu thành chunks
        chunks = []
        current_chunk = ""
        sentences_in_chunk = 0
        
        print(f"   🔨 Bắt đầu ghép {len(sentences)} câu thành chunks (max {max_tokens} tokens)...")
        
        for idx, sentence in enumerate(sentences, 1):
            if not sentence:
                continue
            
            # Thử thêm câu vào chunk hiện tại
            test_chunk = current_chunk + ("\n" if current_chunk and '\n' in text else " " if current_chunk else "") + sentence
            test_tokens = self._build_source_tokens(test_chunk)
            
            if len(test_tokens) > max_tokens:
                # Chunk hiện tại đã đủ lớn, lưu lại
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    print(f"      → Chunk {len(chunks)}: {sentences_in_chunk} câu, {len(current_chunk)} ký tự")
                    current_chunk = sentence
                    sentences_in_chunk = 1
                else:
                    # Câu đơn quá dài, buộc phải cắt theo từ
                    print(f"      ⚠️ Câu {idx} quá dài ({len(sentence)} ký tự), chia nhỏ hơn...")
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        test_word = temp_chunk + (" " if temp_chunk else "") + word
                        if len(self._build_source_tokens(test_word)) > max_tokens:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                print(f"      → Chunk {len(chunks)}: từ bị cắt, {len(temp_chunk)} ký tự")
                                temp_chunk = word
                            else:
                                # Từ đơn quá dài, thêm vào luôn
                                chunks.append(word)
                                print(f"      → Chunk {len(chunks)}: 1 từ dài, {len(word)} ký tự")
                                temp_chunk = ""
                        else:
                            temp_chunk = test_word
                    
                    if temp_chunk:
                        current_chunk = temp_chunk
                        sentences_in_chunk = 1
            else:
                current_chunk = test_chunk
                sentences_in_chunk += 1
        
        # Thêm chunk cuối
        if current_chunk and current_chunk.strip():
            chunks.append(current_chunk.strip())
            print(f"      → Chunk {len(chunks)} (cuối): {sentences_in_chunk} câu, {len(current_chunk)} ký tự")
        
        total_chunk_chars = sum(len(c) for c in chunks)
        print(f"   ✅ Tổng kết chia văn bản:")
        print(f"      - Input: {len(text)} ký tự")
        print(f"      - Output: {len(chunks)} chunks, {total_chunk_chars} ký tự")
        print(f"      - Mất: {len(text) - total_chunk_chars} ký tự ({(len(text)-total_chunk_chars)/len(text)*100:.1f}%)")
        
        return chunks if chunks else [text]

    def _translate_stage1(self, source_text: str) -> str:
        assert self.tokenizer is not None
        assert self.translator is not None

        # Kiểm tra độ dài và chia nhỏ nếu cần
        test_tokens = self._build_source_tokens(source_text)
        
        # Nếu văn bản quá dài, chia nhỏ
        if len(test_tokens) > 500:
            print(f"\n   ⚠️  Văn bản dài ({len(test_tokens)} tokens, {len(source_text)} ký tự)")
            print(f"   📋 Đang chia nhỏ văn bản...")
            chunks = self._split_text(source_text)
            print(f"   📦 Đã chia thành {len(chunks)} đoạn")
            
            # Kiểm tra tổng độ dài chunks
            total_chunk_length = sum(len(c) for c in chunks)
            print(f"   📏 Tổng độ dài chunks: {total_chunk_length} ký tự (gốc: {len(source_text)} ký tự)")
            
            if total_chunk_length < len(source_text) - 10:
                print(f"   ⚠️  CẢNH BÁO: Mất {len(source_text) - total_chunk_length} ký tự khi chia!")
            
            translated_chunks = []
            
            for i, chunk in enumerate(chunks, 1):
                chunk_preview = chunk[:50] + "..." if len(chunk) > 50 else chunk
                print(f"\n   🔄 Đoạn {i}/{len(chunks)}: {len(chunk)} ký tự")
                print(f"      Preview: {chunk_preview}")
                
                # Xử lý token theo loại model
                chunk_tokens = self._build_source_tokens(chunk)
                print(f"      First 5 tokens: {chunk_tokens[:5]}")

                print(f"      Tokens: {len(chunk_tokens)}")
                
                # Tính toán max_decoding_length dựa trên độ dài input
                # Tiếng Việt thường dài hơn tiếng Anh 1.2-1.5 lần
                estimated_output_length = int(len(chunk_tokens) * 1.5) + 50
                max_length = max(min(estimated_output_length, 2048), 512)
                
                print(f"      Max output length: {max_length} tokens")
                
                # Debug: Hiển thị vài token đầu để kiểm tra
                print(f"      Input tokens (first 10): {chunk_tokens[:10]}")
                
                # Chuẩn bị target prefix nếu có token tiếng Việt
                target_prefix = None
                if hasattr(self, 'model_type') and self.model_type == "m2m100":
                    vi_token = self._get_lang_token("vi")
                    if vi_token:
                        target_prefix = [[vi_token]]
                        print(f"      Target prefix (M2M100): {target_prefix}")
                
                translate_kwargs = {
                    "beam_size": self.beam_size,
                    "max_decoding_length": max_length,
                    "min_decoding_length": int(len(chunk_tokens) * 0.8),
                    "repetition_penalty": 1.2,
                    "no_repeat_ngram_size": 3,
                    "return_scores": False,
                }
                if target_prefix:
                    translate_kwargs["target_prefix"] = target_prefix

                results = self.translator.translate_batch(
                    [chunk_tokens],
                    **translate_kwargs,
                )
                
                target_tokens = results[0].hypotheses[0]
                print(f"      Output tokens: {len(target_tokens)}")
                print(f"      Output tokens (first 20): {target_tokens[:20]}")
                
                target_text = self.tokenizer.decode(
                    self.tokenizer.convert_tokens_to_ids(target_tokens),
                    skip_special_tokens=True,
                )
                
                # Kiểm tra xem có phải tiếng Việt không
                vietnamese_chars = sum(1 for c in target_text if ord(c) > 127)
                print(f"      Vietnamese chars: {vietnamese_chars}/{len(target_text)}")
                
                if not target_text or not target_text.strip():
                    print(f"      ⚠️  CẢNH BÁO: Đoạn {i} dịch ra rỗng!")
                else:
                    translated_chunks.append(target_text.strip())
                    translation_preview = target_text[:50] + "..." if len(target_text) > 50 else target_text
                    ratio = len(target_text) / len(chunk) * 100
                    print(f"      ✓ Output: {len(target_text)} ký tự ({ratio:.1f}% input)")
                    print(f"      Preview: {translation_preview}")
                    
                    # Cảnh báo nếu output không phải tiếng Việt
                    if vietnamese_chars < len(target_text) * 0.1:
                        print(f"      ⚠️  CẢNH BÁO: Bản dịch có vẻ KHÔNG PHẢI tiếng Việt!")
                    
                    # Cảnh báo nếu output quá ngắn
                    if ratio < 50:
                        print(f"      ⚠️  CẢNH BÁO: Bản dịch có vẻ ngắn bất thường!")
            
            full_translation = " ".join(translated_chunks)
            print(f"\n   ✅ Tổng kết:")
            print(f"      - Input: {len(source_text)} ký tự")
            print(f"      - Chunks: {len(chunks)} đoạn")
            print(f"      - Output: {len(full_translation)} ký tự")
            print(f"      - Tỷ lệ: {len(full_translation)/len(source_text)*100:.1f}%")
            return full_translation
        
        # Văn bản ngắn, dịch trực tiếp
        source_tokens = self._build_source_tokens(source_text)
        
        estimated_output_length = int(len(test_tokens) * 1.5) + 50
        max_length = max(min(estimated_output_length, 2048), 512)
        
        # Chuẩn bị target_prefix để force tiếng Việt
        target_prefix = None
        if hasattr(self, 'model_type') and self.model_type == "m2m100":
            vi_token = self._get_lang_token("vi")
            if vi_token:
                target_prefix = [[vi_token]]
        elif hasattr(self, 'model_type') and self.model_type == "opus":
            if hasattr(self.tokenizer, 'lang_code_to_id') and 'vi' in self.tokenizer.lang_code_to_id:
                vi_token_id = self.tokenizer.lang_code_to_id['vi']
                target_prefix = [[self.tokenizer.convert_ids_to_tokens([vi_token_id])[0]]]

        translate_kwargs = {
            "beam_size": self.beam_size,
            "max_decoding_length": max_length,
            "min_decoding_length": int(len(test_tokens) * 0.8),
            "repetition_penalty": 1.2,
            "no_repeat_ngram_size": 3,
        }
        if target_prefix:
            translate_kwargs["target_prefix"] = target_prefix

        results = self.translator.translate_batch(
            [source_tokens],
            **translate_kwargs,
        )

        target_tokens = results[0].hypotheses[0]
        target_text = self.tokenizer.decode(
            self.tokenizer.convert_tokens_to_ids(target_tokens),
            skip_special_tokens=True,
        )

        return target_text

    def _refine_stage2(self, source_text: str, raw_translation: str) -> str:
        prompt = f"""Cải thiện bản dịch tiếng Việt sau để nghe tự nhiên và mượt mà hơn.

YÊU CẦU QUAN TRỌNG:
1. Giữ NGUYÊN các danh từ riêng, tên công ty, tên sản phẩm, thuật ngữ chuyên ngành bằng tiếng Anh
2. Sau các thuật ngữ tiếng Anh, thêm bản dịch tạm trong ngoặc đơn. Ví dụ: "GeoCity (ứng dụng địa lý)", "Computer Club (Câu lạc bộ Máy tính)"
3. Làm cho văn bản nghe tự nhiên, mượt mà như người Việt nói
4. Giữ nguyên ý nghĩa và phong cách của văn bản gốc

Văn bản tiếng Anh gốc: {source_text}

Bản dịch hiện tại: {raw_translation}

Bản dịch cải tiến:"""

        estimated_tokens = len(raw_translation) // 2 + 500
        max_tokens = min(max(estimated_tokens, 2048), 16384)

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "system": (
                        "Bạn là một biên tập viên chuyên nghiệp về dịch thuật tiếng Việt. "
                        "Nhiệm vụ của bạn là cải thiện bản dịch để nghe tự nhiên, mượt mà như người Việt bản xứ. "
                        "Luôn GIỮ NGUYÊN các thuật ngữ tiếng Anh (tên riêng, tên công ty, sản phẩm, thuật ngữ kỹ thuật) "
                        "và thêm bản dịch tạm trong ngoặc đơn ngay sau đó. "
                        "CHỈ trả về văn bản tiếng Việt đã được cải thiện, KHÔNG giải thích hay bình luận gì thêm."
                    ),
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": max_tokens,
                        "stop": ["English:", "Original:", "Source:", "Note:", "Văn bản tiếng Anh:", "Bản dịch hiện tại:"],
                    },
                },
                timeout=600,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama API lỗi: {response.status_code}")

            result = response.json()
            refined_text = result.get("response", "").strip()

            # Loại bỏ các prefix không mong muốn
            prefixes_to_remove = [
                "Bản dịch cải tiến:",
                "Bản dịch:",
                "Improved Vietnamese:",
                "Improved:",
                "Translation:",
                "Vietnamese:",
            ]
            for prefix in prefixes_to_remove:
                if refined_text.startswith(prefix):
                    refined_text = refined_text[len(prefix):].strip()

            return refined_text if refined_text else raw_translation

        except requests.exceptions.Timeout as exc:
            raise TimeoutError("Ollama API timeout. Thử lại hoặc tăng timeout.") from exc
        except Exception as exc:
            raise RuntimeError(f"Lỗi khi gọi Ollama: {exc}") from exc

    def _translate_with_ollama_only(self, source_text: str) -> str:
        """Dịch trực tiếp bằng Ollama (chậm hơn nhưng chất lượng tốt)."""
        prompt = f"""Dịch văn bản tiếng Anh sau sang tiếng Việt một cách tự nhiên và mượt mà.

YÊU CẦU:
1. GIỮ NGUYÊN các danh từ riêng, tên công ty, sản phẩm, thuật ngữ chuyên ngành bằng tiếng Anh
2. Sau thuật ngữ tiếng Anh, thêm bản dịch tạm trong ngoặc đơn
3. Dịch tự nhiên như người Việt nói, không dịch sát từng từ
4. KHÔNG lặp lại nội dung, mỗi ý chỉ dịch MỘT LẦN

Văn bản tiếng Anh:
{source_text}

Bản dịch tiếng Việt:"""

        estimated_tokens = len(source_text) // 2 + 500
        max_tokens = min(max(estimated_tokens, 2048), 16384)

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "system": (
                        "Bạn là một dịch giả chuyên nghiệp Anh-Việt. "
                        "Dịch chính xác, tự nhiên, không lặp lại nội dung. "
                        "Giữ nguyên thuật ngữ tiếng Anh và thêm bản dịch trong ngoặc. "
                        "CHỈ trả về bản dịch, KHÔNG giải thích."
                    ),
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": max_tokens,
                        "repeat_penalty": 1.2,
                        "stop": ["English:", "Văn bản tiếng Anh:", "\n\nEnglish", "\n\nVăn bản"],
                    },
                },
                timeout=600,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama API lỗi: {response.status_code}")

            result = response.json()
            translation = result.get("response", "").strip()

            # Loại bỏ prefix
            prefixes = ["Bản dịch tiếng Việt:", "Bản dịch:", "Translation:"]
            for prefix in prefixes:
                if translation.startswith(prefix):
                    translation = translation[len(prefix):].strip()

            return translation

        except Exception as exc:
            raise RuntimeError(f"Lỗi khi gọi Ollama: {exc}") from exc

    def translate_and_refine(self, text_to_translate: str) -> Dict:
        if not text_to_translate or not text_to_translate.strip():
            return {
                "source": "",
                "raw_translation": "",
                "refined_translation": "",
                "time_stage1_sec": 0.0,
                "time_stage2_sec": 0.0,
                "error": "Văn bản đầu vào trống",
            }

        # Nếu chỉ dùng Ollama, dịch trực tiếp
        if self.use_ollama_only:
            start = time.time()
            try:
                translation = self._translate_with_ollama_only(text_to_translate)
                end = time.time()
                return {
                    "source": text_to_translate,
                    "raw_translation": translation,
                    "refined_translation": translation,
                    "time_stage1_sec": end - start,
                    "time_stage2_sec": 0.0,
                }
            except Exception as exc:
                return {
                    "source": text_to_translate,
                    "raw_translation": "",
                    "refined_translation": "",
                    "time_stage1_sec": 0.0,
                    "time_stage2_sec": 0.0,
                    "error": f"Lỗi Ollama: {exc}",
                }

        # Pipeline bình thường (2 giai đoạn)
        start_s1 = time.time()
        try:
            raw_translation = self._translate_stage1(text_to_translate)
        except Exception as exc:
            return {
                "source": text_to_translate,
                "raw_translation": "",
                "refined_translation": "",
                "time_stage1_sec": 0.0,
                "time_stage2_sec": 0.0,
                "error": f"Lỗi Giai đoạn 1: {exc}",
            }
        end_s1 = time.time()

        start_s2 = time.time()
        try:
            refined_translation = self._refine_stage2(text_to_translate, raw_translation)
        except Exception as exc:
            return {
                "source": text_to_translate,
                "raw_translation": raw_translation,
                "refined_translation": "",
                "time_stage1_sec": end_s1 - start_s1,
                "time_stage2_sec": 0.0,
                "error": f"Lỗi Giai đoạn 2: {exc}",
            }
        end_s2 = time.time()

        return {
            "source": text_to_translate,
            "raw_translation": raw_translation,
            "refined_translation": refined_translation,
            "time_stage1_sec": end_s1 - start_s1,
            "time_stage2_sec": end_s2 - start_s2,
        }


def load_config(config_path: Optional[str] = None) -> Dict:
    if config_path is None:
        config_path = CONFIG_DIR / "settings.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Không tìm thấy config tại: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_pipeline_from_config(config_path: Optional[str] = None) -> HybridTranslationPipelineOllama:
    config = load_config(config_path)

    repo_root = Path(__file__).resolve().parents[2]
    ct2_dir = repo_root / config["stage1_model_dir"]

    return HybridTranslationPipelineOllama(
        ct2_model_dir=str(ct2_dir),
        hf_model_name=config["stage1_hf_name"],
        ollama_model=config.get("ollama_model", "llama3:8b"),
        ollama_host=config.get("ollama_host", "http://localhost:11434"),
        temperature=config.get("temperature", 0.2),
        beam_size=config.get("beam_size", 2),
        use_ollama_only=config.get("use_ollama_only", False),
    )


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO: PIPELINE DỊCH THUẬT LAI (OLLAMA)")
    print("=" * 70)

    try:
        pipeline = create_pipeline_from_config()
    except Exception as exc:  # pragma: no cover - manual demo
        print(f"\n❌ Lỗi khởi tạo pipeline:\n{exc}")
        print("\n💡 Hãy chạy: python scripts/setup_models.py")
        print("💡 Và đảm bảo Ollama đang chạy")
        sys.exit(1)

    test_texts = [
        "Hello world! This is a test of the translation system.",
        "The enterprise solution must be robust and scalable.",
        "Artificial intelligence is transforming the way we work.",
    ]

    for idx, text in enumerate(test_texts, 1):
        print(f"\n{'=' * 70}")
        print(f"VĂN BẢN THỬ NGHIỆM #{idx}")
        print(f"{'=' * 70}")

        result = pipeline.translate_and_refine(text)

        if "error" in result:
            print(f"❌ LỖI: {result['error']}")
            continue

        print("\n📝 Nguồn:")
        print(f"   {result['source']}")
        print(f"\n🔄 Thô (Giai đoạn 1 - {result['time_stage1_sec']:.3f}s):")
        print(f"   {result['raw_translation']}")
        print(f"\n✨ Tinh chỉnh (Giai đoạn 2 - {result['time_stage2_sec']:.3f}s):")
        print(f"   {result['refined_translation']}")
        print(
            f"\n⏱️  Tổng thời gian: {result['time_stage1_sec'] + result['time_stage2_sec']:.3f}s"
        )

    print(f"\n{'=' * 70}")
    print("✅ DEMO HOÀN TẤT")
    print("=" * 70)
