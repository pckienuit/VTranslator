@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
pushd "%~dp0.."

echo ================================================================
echo      THIET LAP CONG CU DICH GEMMA 3 12B (OLLAMA)
echo ================================================================
echo.
echo Script nay se tu dong:
echo   1. Kiem tra Python va pip
echo   2. Cai dat cac thu vien Python can thiet
echo   3. Huong dan tai model Gemma 3 12B qua Ollama
echo   4. Goi y chay ung dung
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
echo BUOC 2: Cai dat thu vien Python
echo ================================================================
echo Dang cai dat cac thu vien trong requirements.txt ...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi khi cài đặt thư viện!
    pause
    popd
    exit /b 1
)
echo ✅ Các thư viện đã được cài đặt

echo.
echo ================================================================
echo BUOC 3: Huong dan Ollama / Gemma 3 12B
echo ================================================================
echo.
echo    1. Cai dat Ollama: https://ollama.ai/download
echo    2. Mo Command Prompt va chay:
echo       ollama pull gemma3:12b
echo       ollama serve
echo    3. Khi Ollama san sang, chay:
echo       python run_app.py
echo.
echo 💡 Ollama chi tai model lan dau. Nhung lan sau co the su dung ngay.

echo.
echo ================================================================
echo ✅ HOAN TAT THIET LAP
echo ================================================================
echo Tiep tuc bang cach mo Ollama va chay python run_app.py
echo Xem docs\OLLAMA_GUIDE.md neu can them thong tin.
echo.
popd
pause
