"""Legacy stub kept for backward compatibility."""


def main() -> None:  # pragma: no cover - simple CLI notice
    print("=" * 70)
    print("M2M100 SETUP (DEPRECATED)")
    print("=" * 70)
    print(
        "Pipeline hiện chỉ sử dụng Gemma 3 12B thông qua Ollama, nên không cần cài đặt M2M100/CTranslate2 nữa."
    )
    print("\nNếu bạn cần dịch đa ngôn ngữ bằng NMT, hãy tự tách logic đó trong một repo khác.")


if __name__ == "__main__":
    main()
