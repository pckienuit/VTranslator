"""Script để tải và chuyển đổi mô hình M2M100 (Facebook) sang CTranslate2."""

import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

def main():
    """Tải và chuyển đổi M2M100."""
    try:
        import ctranslate2
        import transformers
    except ImportError as exc:
        print("❌ Lỗi: Chưa cài đặt thư viện cần thiết")
        print("\nChạy: pip install ctranslate2 transformers sentencepiece")
        sys.exit(1)

    print("=" * 70)
    print("SETUP MÔ HÌNH M2M100 (FACEBOOK)")
    print("=" * 70)
    
    # Chọn model size
    print("\nChọn kích thước mô hình:")
    print("1. m2m100_418M (Nhỏ, nhanh - Đề xuất)")
    print("2. m2m100_1.2B (Lớn, chất lượng cao hơn)")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == "1":
        model_name = "facebook/m2m100_418M"
        output_dir = "models/m2m100-418m-ct2"
    elif choice == "2":
        model_name = "facebook/m2m100_1.2B"
        output_dir = "models/m2m100-1.2b-ct2"
    else:
        print("❌ Lựa chọn không hợp lệ!")
        sys.exit(1)
    
    output_path = REPO_ROOT / output_dir
    
    print(f"\n📦 Mô hình: {model_name}")
    print(f"📁 Thư mục output: {output_path}")
    
    if output_path.exists():
        print(f"\n⚠️  Thư mục {output_path} đã tồn tại.")
        overwrite = input("Ghi đè? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Hủy bỏ.")
            sys.exit(0)
    
    # Tạo thư mục
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("BƯỚC 1: TẢI MÔ HÌNH TỪ HUGGING FACE")
    print("=" * 70)
    print("⏳ Đang tải... (có thể mất vài phút)")
    
    try:
        # Tải model từ HuggingFace
        print(f"Downloading {model_name}...")
        model = transformers.M2M100ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = transformers.M2M100Tokenizer.from_pretrained(model_name)
        print("✅ Đã tải mô hình!")
    except Exception as exc:
        print(f"❌ Lỗi khi tải mô hình: {exc}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("BƯỚC 2: CHUYỂN ĐỔI SANG CTRANSLATE2")
    print("=" * 70)
    print("⏳ Đang chuyển đổi...")
    
    try:
        # Lưu tạm để convert
        temp_dir = output_path.parent / f"{output_path.name}_temp"
        temp_dir.mkdir(exist_ok=True)
        
        model.save_pretrained(str(temp_dir))
        tokenizer.save_pretrained(str(temp_dir))
        
        # Convert sang CTranslate2
        converter = ctranslate2.converters.TransformersConverter(str(temp_dir))
        converter.convert(str(output_path), quantization="int8")
        
        # Xóa thư mục tạm
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ Chuyển đổi thành công!")
    except Exception as exc:
        print(f"❌ Lỗi khi chuyển đổi: {exc}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ HOÀN TẤT!")
    print("=" * 70)
    print(f"\nMô hình đã được cài đặt tại: {output_path}")
    print("\nĐể sử dụng mô hình này, cập nhật src/config/settings.json:")
    print(f"""
{{
  "stage1_model_dir": "{output_dir}",
  "stage1_hf_name": "{model_name}",
  ...
}}
    """)
    print("\nLưu ý: M2M100 cần token đặc biệt cho ngôn ngữ:")
    print("  - Source: '__en__' (tiếng Anh)")
    print("  - Target: '__vi__' (tiếng Việt)")
    print("\nBạn cần cập nhật code để thêm các token này.")

if __name__ == "__main__":
    main()
