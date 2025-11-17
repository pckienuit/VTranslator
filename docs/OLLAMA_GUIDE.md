# Ollama Setup Guide

Use this guide to prepare your local environment to run the single-stage Gemma translator.

## 1. Install Ollama
1. Download the latest installer from https://ollama.com/download
2. Run the installer and follow the prompts
3. After installation, ensure the `ollama` command works in a new terminal

## 2. Pull the Gemma model
```cmd
ollama pull gemma3:12b
```
This may take several minutes depending on your connection.

## 3. Configure server access (optional)
If you plan to run Ollama on a different machine, edit `src/config/settings.json` and adjust `ollama_host`. For HTTPS endpoints add the proper scheme, e.g. `https://ollama.example.com`.

## 4. Verify the model
```cmd
ollama run gemma3:12b "Hello"
```
If you see a response the model is ready.

## 5. Launch the translator
From the project root:
```cmd
python run_app.py
```
Then open the printed Gradio URL. Provide both the original text and context/instructions, and press "Translate".
