@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
pushd "%~dp0.."

echo ================================================================
echo      THIẾT LẬP TỰ ĐỘNG PIPELINE DỊCH THUẬT LAI - OLLAMA
echo ================================================================
echo.
echo Script này sẽ tự động:
echo   1. Kiểm tra Python và pip
echo   2. Cài đặt các thư viện cần thiết
echo   3. Tải và chuyển đổi mô hình Stage 1 (CTranslate2)
echo   4. Hướng dẫn cài đặt Ollama và chạy ứng dụng
pause

echo.
echo ================================================================
echo BƯỚC 1: Kiểm tra Python
echo ================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Lỗi: Không tìm thấy Python!
    echo    Hãy cài đặt Python từ: https://www.python.org/downloads/
    echo    Đảm bảo chọn "Add Python to PATH" khi cài đặt.
    pause
    popd
    exit /b 1
)
echo ✅ Python đã được cài đặt

echo.
echo ================================================================
echo BƯỚC 2: Cài đặt thư viện Python
echo ================================================================
echo Đang cài đặt: ctranslate2, transformers, sentencepiece, gradio, requests, torch...
pip install ctranslate2 transformers sentencepiece gradio requests torch
if errorlevel 1 (
    echo ❌ Lỗi khi cài đặt thư viện!
    pause
    popd
    exit /b 1
)
echo ✅ Các thư viện đã được cài đặt

echo.
echo ================================================================
echo BƯỚC 3: Thiết lập mô hình Stage 1 (CTranslate2)
echo ================================================================
python scripts\setup_models.py
if errorlevel 1 (
    echo ❌ Lỗi khi thiết lập mô hình Stage 1!
    pause
    popd
    exit /b 1
)

echo.
echo ================================================================
echo BƯỚC 4: Hướng dẫn cài đặt Ollama (Stage 2)
echo ================================================================
echo.
echo 📋 Ollama sẽ quản lý mô hình LLM Stage 2.
echo.
echo ✅ Các bước tiếp theo:
echo.
echo    1. Tải Ollama từ: https://ollama.ai/download
echo       (Chọn phiên bản Windows)
echo.
echo    2. Cài đặt Ollama (chạy file .exe đã tải)
echo.
echo    3. Mở Command Prompt hoặc Terminal và chạy:
echo       ollama pull llama3.2:3b
echo.
echo    4. Khởi động dịch vụ Ollama:
echo       ollama serve
echo.
echo    5. Chạy ứng dụng dịch thuật:
echo       python run_app.py
echo.
echo 💡 Ollama sẽ tự động tải mô hình ~2GB lần đầu chạy 'pull'.
echo    Sau đó mô hình được cache và sẵn sàng sử dụng.

echo.
echo ================================================================
echo ✅ HOÀN TẤT THIẾT LẬP STAGE 1
echo ================================================================
echo Mô hình dịch thô (Stage 1) đã sẵn sàng!
echo Hãy làm theo hướng dẫn ở trên để cài đặt Ollama.
echo.
echo 📖 Xem thêm: docs\OLLAMA_GUIDE.md
echo.
popd
pause
